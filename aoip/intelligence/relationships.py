from __future__ import annotations

from aoip.models import Conversation


ROLE_KEYWORDS = {
    "investor": ["investor", "vc", "venture", "capital"],
    "founder": ["founder", "ceo", "startup"],
    "policy maker": ["minister", "regulator", "government", "policy"],
    "journalist": ["journalist", "editor", "media"],
    "researcher": ["researcher", "professor", "paper", "study"],
}


def recommended_relationship_action(conversation: Conversation) -> str:
    text = f"{conversation.title} {conversation.summary} {conversation.content}".lower()
    role = "ecosystem builder"
    for candidate, keywords in ROLE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            role = candidate
            break
    if conversation.relationship_score >= 75:
        return f"Prioritize warm outreach. Potential {role}, speaker, interview guest, or partner."
    if conversation.relationship_score >= 55:
        return f"Engage publicly with a useful comment and save as a potential {role}."
    return "Monitor; no direct outreach needed yet."
