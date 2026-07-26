from __future__ import annotations

import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aoip.config import BACKUP_DIR, DATA_DIR, ensure_directories
from aoip.models import Base, SourceConfig


DB_PATH = DATA_DIR / "aoip.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, future=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    ensure_directories()
    Base.metadata.create_all(engine)
    seed_defaults()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def seed_defaults() -> None:
    defaults = [
        ("Google News Africa Business", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20business%20innovation"),
        ("Google News African Startups", "google_news_rss", "https://news.google.com/rss/search?q=African%20startups%20funding"),
        ("World Bank Africa", "rss", "https://blogs.worldbank.org/en/africacan/rss.xml"),
        ("African Development Bank", "rss", "https://www.afdb.org/en/news-and-events/rss.xml"),
    ]
    with SessionLocal() as session:
        for name, kind, url in defaults:
            exists = session.query(SourceConfig).filter(SourceConfig.name == name).first()
            if not exists:
                session.add(SourceConfig(name=name, kind=kind, url=url))
        session.commit()


def backup_database() -> Path | None:
    ensure_directories()
    if not DB_PATH.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"aoip-{stamp}.sqlite3"
    shutil.copy2(DB_PATH, target)
    return target
