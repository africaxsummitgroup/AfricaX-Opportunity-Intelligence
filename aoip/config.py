from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = DATA_DIR / "backups"
EXPORT_DIR = DATA_DIR / "exports"
CHROMA_DIR = DATA_DIR / "chroma"
SETTINGS_FILE = DATA_DIR / "settings.json"


@dataclass(slots=True)
class AppSettings:
    openai_api_key: str = ""
    openai_model: str = "gpt-5.5"
    embedding_model: str = "text-embedding-3-large"
    google_api_key: str = ""
    google_cse_id: str = ""
    default_countries: str = "Nigeria, Kenya, South Africa, Ghana, Egypt, Rwanda, Ethiopia, Morocco"
    default_industries: str = "AI, fintech, climate, manufacturing, trade, infrastructure, payments, healthcare, education, agriculture, gaming, creator economy, investment"
    scan_depth: int = 20
    offline_demo_mode: bool = True

    @property
    def countries(self) -> list[str]:
        return [item.strip() for item in self.default_countries.split(",") if item.strip()]

    @property
    def industries(self) -> list[str]:
        return [item.strip() for item in self.default_industries.split(",") if item.strip()]


def ensure_directories() -> None:
    for directory in [DATA_DIR, BACKUP_DIR, EXPORT_DIR, CHROMA_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def load_settings() -> AppSettings:
    ensure_directories()
    payload: dict[str, Any] = {}
    if SETTINGS_FILE.exists():
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))

    settings = AppSettings(**{k: v for k, v in payload.items() if hasattr(AppSettings, k)})
    settings.openai_api_key = os.getenv("OPENAI_API_KEY", settings.openai_api_key)
    settings.google_api_key = os.getenv("GOOGLE_API_KEY", settings.google_api_key)
    settings.google_cse_id = os.getenv("GOOGLE_CSE_ID", settings.google_cse_id)
    return settings


def save_settings(settings: AppSettings) -> None:
    ensure_directories()
    SETTINGS_FILE.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
