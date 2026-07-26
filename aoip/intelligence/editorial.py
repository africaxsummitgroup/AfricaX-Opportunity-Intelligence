from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from aoip.ai import AIClient


PILLARS = {
    "Business Opportunity": ["market", "opportunity", "growth", "expansion", "trade"],
    "Innovation": ["innovation", "startup", "product", "technology", "ai"],
    "Entrepreneurship": ["founder", "entrepreneur", "sme", "builder"],
    "Investment": ["funding", "investor", "venture", "capital", "acquisition"],
    "Economic Development": ["policy", "government", "infrastructure", "jobs", "development"],
}


@dataclass(slots=True)
class EditorialAssessment:
    summary: str
    country: str
    industry: str
    pillar: str
    opportunity_score: float
    relationship_score: float
    authority_score: float
    recommended_action: str
    suggested_comment: str
    follow_up_question: str


def assess_conversation(title: str, body: str, countries: list[str], industries: list[str], ai: AIClient) -> EditorialAssessment:
    text = f"{title}\n{body}".strip()
    fallback = _heuristic_assessment(text, countries, industries)
    payload = ai.complete_json(
        system=(
            "You are AfricaX's editorial intelligence analyst. Return concise JSON with keys: "
            "summary, country, industry, pillar, opportunity_score, relationship_score, "
            "authority_score, recommended_action, suggested_comment, follow_up_question."
        ),
        user=text[:8000],
        fallback=asdict(fallback),
    )
    return EditorialAssessment(
        summary=str(payload.get("summary", fallback.summary)),
        country=str(payload.get("country", fallback.country)),
        industry=str(payload.get("industry", fallback.industry)),
        pillar=str(payload.get("pillar", fallback.pillar)),
        opportunity_score=float(payload.get("opportunity_score", fallback.opportunity_score)),
        relationship_score=float(payload.get("relationship_score", fallback.relationship_score)),
        authority_score=float(payload.get("authority_score", fallback.authority_score)),
        recommended_action=str(payload.get("recommended_action", fallback.recommended_action)),
        suggested_comment=str(payload.get("suggested_comment", fallback.suggested_comment)),
        follow_up_question=str(payload.get("follow_up_question", fallback.follow_up_question)),
    )


def _heuristic_assessment(text: str, countries: list[str], industries: list[str]) -> EditorialAssessment:
    lower = text.lower()
    country = next((item for item in countries if item.lower() in lower), "Africa")
    industry = next((item for item in industries if item.lower() in lower), "business opportunity")
    pillar = _pillar_for_text(lower)
    hot_words = ["funding", "launch", "policy", "expansion", "ai", "investment", "acquisition", "infrastructure"]
    question_count = len(re.findall(r"\?", text))
    opportunity = min(100.0, 35 + 8 * sum(word in lower for word in hot_words) + 3 * question_count)
    relationship = min(100.0, 30 + 12 * sum(word in lower for word in ["founder", "investor", "minister", "journalist", "researcher"]))
    authority = min(100.0, 40 + 10 * sum(word in lower for word in ["poorly understood", "why", "how", "guide", "framework", "report"]))
    action = "publish" if opportunity >= 70 else "investigate" if opportunity >= 55 else "engage" if relationship >= 55 else "monitor"
    summary = text[:220].replace("\n", " ").strip() or "No summary available."
    return EditorialAssessment(
        summary=summary,
        country=country,
        industry=industry,
        pillar=pillar,
        opportunity_score=opportunity,
        relationship_score=relationship,
        authority_score=authority,
        recommended_action=action,
        suggested_comment=(
            "This is a useful signal for Africa's innovation ecosystem. A valuable next step would be to compare "
            "what is changing now with the structural barriers founders and operators still face."
        ),
        follow_up_question=f"What evidence would help operators understand the real opportunity in {country}'s {industry} market?",
    )


def _pillar_for_text(lower_text: str) -> str:
    scores = {pillar: sum(keyword in lower_text for keyword in keywords) for pillar, keywords in PILLARS.items()}
    return max(scores, key=scores.get)
