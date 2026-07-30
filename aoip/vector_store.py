from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aoip.ai import AIClient
from aoip.config import CHROMA_DIR


@dataclass(slots=True)
class SearchHit:
    id: str
    text: str
    metadata: dict[str, Any]
    distance: float


class VectorStore:
    def __init__(self, ai: AIClient):
        self.ai = ai
        self._collection = None
        try:
            import chromadb

            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self._collection = client.get_or_create_collection(name="aoip_knowledge")
        except Exception:
            self._memory: dict[str, tuple[str, dict[str, Any], list[float]]] = {}

    @property
    def is_chroma_enabled(self) -> bool:
        return self._collection is not None

    def upsert(self, item_id: str, text: str, metadata: dict[str, Any]) -> None:
        embedding = self.ai.embed([text])[0]
        if self._collection:
            self._collection.upsert(ids=[item_id], documents=[text], metadatas=[metadata], embeddings=[embedding])
            return
        self._memory[item_id] = (text, metadata, embedding)

    def search(self, query: str, n_results: int = 5) -> list[SearchHit]:
        embedding = self.ai.embed([query])[0]
        if self._collection:
            result = self._collection.query(query_embeddings=[embedding], n_results=n_results)
            hits: list[SearchHit] = []
            ids = result.get("ids", [[]])[0]
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]
            for item_id, doc, meta, distance in zip(ids, docs, metas, distances):
                hits.append(SearchHit(id=item_id, text=doc or "", metadata=meta or {}, distance=float(distance)))
            return hits

        scored = []
        for item_id, (text, metadata, item_embedding) in self._memory.items():
            distance = sum((a - b) ** 2 for a, b in zip(embedding, item_embedding))
            scored.append(SearchHit(item_id, text, metadata, distance))
        return sorted(scored, key=lambda hit: hit.distance)[:n_results]
