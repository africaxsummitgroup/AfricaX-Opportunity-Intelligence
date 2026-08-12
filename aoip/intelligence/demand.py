from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from aoip.connectors.rss import FeedItem


DEMAND_TOPICS = [
    ("Startup funding", "Africa startup funding venture capital grants", "investment"),
    ("AI business opportunities", "AI business opportunities Africa startups", "AI"),
    ("Fintech regulation", "Africa fintech payments regulation central bank", "fintech"),
    ("Climate finance", "Africa climate finance bankable projects carbon markets", "climate"),
    ("AfCFTA trade opportunities", "AfCFTA opportunities small business manufacturing logistics", "trade"),
    ("Manufacturing opportunities", "Africa manufacturing clusters export opportunities", "manufacturing"),
    ("Creator economy", "Africa creator economy monetization platforms", "creator economy"),
    ("Healthtech", "Africa healthtech startups healthcare investment", "healthcare"),
    ("Edtech", "Africa edtech startups education technology", "education"),
    ("Infrastructure investment", "Africa infrastructure investment energy logistics", "infrastructure"),
]


@dataclass(slots=True)
class DemandAssessment:
    demand_score: float
    authority_gap_score: float
    recommended_content: str
    suggested_title: str
    suggested_outline: str


def google_news_rss_for_query(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}"


def google_trends_explore_url(query: str, geo: str = "") -> str:
    geo_part = f"&geo={quote_plus(geo)}" if geo else ""
    return f"https://trends.google.com/trends/explore?date=today%203-m{geo_part}&q={quote_plus(query)}"


def assess_demand(topic: str, query: str, industry: str, items: list[FeedItem]) -> DemandAssessment:
    question_words = ("how", "why", "what", "best", "guide", "opportunities", "funding", "grants")
    evidence_count = len(items)
    question_hits = sum(any(word in item.title.lower() for word in question_words) for item in items)
    demand_score = min(100.0, 35 + evidence_count * 8 + question_hits * 6)
    authority_gap_score = min(100.0, 45 + question_hits * 8 + (15 if evidence_count < 4 else 0))
    recommended_content = "research brief" if demand_score >= 75 else "explainer article" if demand_score >= 60 else "monitoring note"
    suggested_title = f"What AfricaX should explain about {topic.lower()} now"
    suggested_outline = (
        "1. What people are trying to understand\n"
        "2. Why the topic is rising now\n"
        "3. Key markets, companies, and policy signals\n"
        "4. Practical opportunities and risks\n"
        "5. What AfricaX should watch next"
    )
    return DemandAssessment(
        demand_score=demand_score,
        authority_gap_score=authority_gap_score,
        recommended_content=recommended_content,
        suggested_title=suggested_title,
        suggested_outline=suggested_outline,
    )
