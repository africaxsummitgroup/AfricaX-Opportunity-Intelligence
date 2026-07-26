from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from aoip.config import EXPORT_DIR, ensure_directories
from aoip.models import Conversation, OpportunityReport


def daily_brief(conversations: list[Conversation]) -> str:
    top = sorted(conversations, key=lambda item: item.opportunity_score, reverse=True)[:8]
    lines = [
        f"# AfricaX Daily Intelligence Brief - {datetime.now():%Y-%m-%d}",
        "",
        "## Highest-Leverage Recommendation",
        _highest_leverage(top),
        "",
        "## Priority Signals",
    ]
    for item in top:
        lines.extend(
            [
                f"### {item.title}",
                f"- Source: {item.source}",
                f"- Country: {item.country or 'Africa'}",
                f"- Industry: {item.industry or 'General'}",
                f"- Opportunity Score: {item.opportunity_score:.0f}",
                f"- Recommended Action: {item.recommended_action}",
                f"- Why it matters: {item.summary}",
                "",
            ]
        )
    return "\n".join(lines)


def content_gap_report(reports: list[OpportunityReport]) -> str:
    lines = [f"# AfricaX Content Gap Report - {datetime.now():%Y-%m-%d}", ""]
    for report in sorted(reports, key=lambda item: item.authority_impact, reverse=True):
        lines.extend(
            [
                f"## {report.title}",
                f"- Topic: {report.topic}",
                f"- Audience: {report.audience}",
                f"- Difficulty: {report.difficulty}",
                f"- Authority Impact: {report.authority_impact:.0f}",
                "",
                "### Why Demand Exists",
                report.why_now,
                "",
                "### Evidence",
                report.evidence,
                "",
                "### Suggested Outline",
                report.outline,
                "",
            ]
        )
    return "\n".join(lines)


def export_markdown(title: str, markdown: str) -> Path:
    ensure_directories()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in title.lower()).strip("-")
    path = EXPORT_DIR / f"{safe}-{datetime.now():%Y%m%d-%H%M%S}.md"
    path.write_text(markdown, encoding="utf-8")
    return path


def export_conversations_csv(conversations: list[Conversation]) -> Path:
    ensure_directories()
    path = EXPORT_DIR / f"conversations-{datetime.now():%Y%m%d-%H%M%S}.csv"
    rows = [
        {
            "title": item.title,
            "source": item.source,
            "country": item.country,
            "industry": item.industry,
            "opportunity_score": item.opportunity_score,
            "relationship_score": item.relationship_score,
            "authority_score": item.authority_score,
            "recommended_action": item.recommended_action,
            "url": item.url,
        }
        for item in conversations
    ]
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def _highest_leverage(conversations: list[Conversation]) -> str:
    if not conversations:
        return "Add sources or run a scan to identify today's highest-leverage move."
    best = conversations[0]
    return (
        f"Focus on **{best.title}**. It has the strongest mix of opportunity, authority impact, "
        f"and relationship value. Recommended action: **{best.recommended_action}**."
    )
