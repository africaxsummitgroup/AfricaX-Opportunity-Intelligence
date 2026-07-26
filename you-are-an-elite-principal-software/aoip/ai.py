from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from aoip.config import AppSettings


@dataclass(slots=True)
class AIResult:
    text: str
    raw: dict[str, Any]


class AIClient:
    def __init__(self, settings: AppSettings):
        self.settings = settings
        self._client = None
        if settings.openai_api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                self._client = None

    @property
    def is_live(self) -> bool:
        return self._client is not None

    def complete_json(self, system: str, user: str, fallback: dict[str, Any]) -> dict[str, Any]:
        if not self._client:
            return fallback
        try:
            response = self._client.responses.create(
                model=self.settings.openai_model,
                input=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                text={"format": {"type": "json_object"}},
            )
            return json.loads(response.output_text)
        except Exception:
            return fallback

    def embed(self, texts: list[str]) -> list[list[float]]:
        if self._client:
            try:
                response = self._client.embeddings.create(model=self.settings.embedding_model, input=texts)
                return [item.embedding for item in response.data]
            except Exception:
                pass
        return [_hash_embedding(text) for text in texts]


def _hash_embedding(text: str, size: int = 384) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = []
    for i in range(size):
        byte = digest[i % len(digest)]
        values.append((byte / 255.0) - 0.5)
    return values
