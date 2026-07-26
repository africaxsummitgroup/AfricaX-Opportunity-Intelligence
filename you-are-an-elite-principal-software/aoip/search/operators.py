from __future__ import annotations

from dataclasses import dataclass
from itertools import product


DEFAULT_SITES = [
    "linkedin.com",
    "reddit.com",
    "substack.com",
    "x.com",
    "youtube.com",
    "github.com",
    "producthunt.com",
    "news.ycombinator.com",
    "quora.com",
]

DEFAULT_INTENTS = [
    "opportunity",
    "startup",
    "funding",
    "market entry",
    "policy",
    "regulation",
    "founder",
    "investor",
    "infrastructure",
    "digital economy",
    "AI",
    "fintech",
    "climate",
    "trade",
]


@dataclass(frozen=True)
class QueryCandidate:
    query: str
    site: str
    country: str
    industry: str
    intent: str


def generate_search_operators(
    countries: list[str],
    industries: list[str],
    sites: list[str] | None = None,
    intents: list[str] | None = None,
    limit: int = 1000,
) -> list[QueryCandidate]:
    active_sites = sites or DEFAULT_SITES
    active_intents = intents or DEFAULT_INTENTS
    queries: list[QueryCandidate] = []
    for site, country, industry, intent in product(active_sites, countries, industries, active_intents):
        query = f"site:{site} {country} {industry} {intent}"
        queries.append(QueryCandidate(query=query, site=site, country=country, industry=industry, intent=intent))
        if len(queries) >= limit:
            break
    return queries
