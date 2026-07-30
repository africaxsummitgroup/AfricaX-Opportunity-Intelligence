from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin


@dataclass(slots=True)
class FeedItem:
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str
    author: str = ""


def fetch_rss(url: str, source_name: str, limit: int = 20) -> list[FeedItem]:
    try:
        import feedparser

        parsed = feedparser.parse(url)
    except Exception:
        return []

    items: list[FeedItem] = []
    base_url = getattr(parsed.feed, "link", url)
    for entry in parsed.entries[:limit]:
        published = None
        if getattr(entry, "published_parsed", None):
            published = datetime(*entry.published_parsed[:6])
        raw_link = getattr(entry, "link", "")
        items.append(
            FeedItem(
                title=getattr(entry, "title", "Untitled"),
                url=urljoin(base_url, raw_link),
                source=source_name,
                published_at=published,
                summary=getattr(entry, "summary", ""),
                author=getattr(entry, "author", ""),
            )
        )
    return items
