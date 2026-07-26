from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote_plus

import requests


@dataclass(slots=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "google"
    published_at: datetime | None = None


def google_news_rss_url(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}"


def google_programmable_search(api_key: str, cse_id: str, query: str, limit: int = 10) -> list[SearchResult]:
    if not api_key or not cse_id:
        return []
    response = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"key": api_key, "cx": cse_id, "q": query, "num": min(limit, 10)},
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    return [
        SearchResult(
            title=item.get("title", "Untitled"),
            url=item.get("link", ""),
            snippet=item.get("snippet", ""),
        )
        for item in payload.get("items", [])
    ]
