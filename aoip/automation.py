from __future__ import annotations

from datetime import datetime

from aoip.ai import AIClient
from aoip.config import AppSettings
from aoip.connectors.rss import fetch_rss
from aoip.db import session_scope
from aoip.intelligence.editorial import assess_conversation
from aoip.models import Conversation, ScanRun, SourceConfig


def run_daily_scan(settings: AppSettings) -> int:
    ai = AIClient(settings)
    found = 0
    with session_scope() as session:
        sources = session.query(SourceConfig).filter(SourceConfig.is_active.is_(True)).all()
        for source in sources:
            if source.kind not in {"rss", "google_news_rss"}:
                continue
            for item in fetch_rss(source.url, source.name, limit=settings.scan_depth):
                exists = session.query(Conversation).filter(Conversation.url == item.url).first()
                if exists:
                    continue
                assessment = assess_conversation(item.title, item.summary, settings.countries, settings.industries, ai)
                session.add(
                    Conversation(
                        title=item.title,
                        url=item.url,
                        source=item.source,
                        published_at=item.published_at,
                        author=item.author,
                        summary=assessment.summary,
                        content=item.summary,
                        country=assessment.country,
                        industry=assessment.industry,
                        pillar=assessment.pillar,
                        opportunity_score=assessment.opportunity_score,
                        relationship_score=assessment.relationship_score,
                        authority_score=assessment.authority_score,
                        recommended_action=assessment.recommended_action,
                        suggested_comment=assessment.suggested_comment,
                        follow_up_question=assessment.follow_up_question,
                    )
                )
                found += 1
        session.add(ScanRun(name=f"Daily scan {datetime.now():%Y-%m-%d %H:%M}", items_found=found))
    return found
