from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from aoip.models import Conversation


QUESTION_STARTERS = ("how ", "why ", "what ", "which ", "where ", "when ", "who ", "can ", "should ")


@dataclass(slots=True)
class GapCandidate:
    topic: str
    demand_score: float
    evidence: str
    suggested_title: str
    outline: str
    audience: str
    difficulty: str
    authority_impact: float


def detect_content_gaps(conversations: Iterable[Conversation]) -> list[GapCandidate]:
    questions: list[str] = []
    topics: Counter[str] = Counter()
    for conversation in conversations:
        text = f"{conversation.title} {conversation.summary} {conversation.content}".lower()
        for sentence in text.replace("?", "?.").split("."):
            clean = sentence.strip()
            if clean.endswith("?") or clean.startswith(QUESTION_STARTERS):
                questions.append(clean.strip("? "))
        if conversation.industry:
            topics[conversation.industry] += 1
        if conversation.country:
            topics[conversation.country] += 1

    candidates: list[GapCandidate] = []
    for topic, count in topics.most_common(8):
        demand = min(100.0, 30 + count * 12)
        candidates.append(
            GapCandidate(
                topic=topic,
                demand_score=demand,
                evidence=f"{count} stored signals mention {topic}. Repeated questions: {len(questions)}.",
                suggested_title=f"The AfricaX guide to {topic}: what matters now and what to watch next",
                outline=(
                    "1. Why this topic matters now\n"
                    "2. Market structure and key actors\n"
                    "3. Common misconceptions\n"
                    "4. Opportunity map\n"
                    "5. What AfricaX should track next"
                ),
                audience="Founders, investors, operators, policy teams, researchers, and ecosystem builders.",
                difficulty="medium",
                authority_impact=min(100.0, demand + 10),
            )
        )
    return candidates
