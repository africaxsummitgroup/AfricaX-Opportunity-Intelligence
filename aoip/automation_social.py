from __future__ import annotations

from datetime import datetime

from aoip.ai import AIClient
from aoip.config import AppSettings
from aoip.connectors.rss import fetch_rss
from aoip.db import session_scope
from aoip.intelligence.demand import DEMAND_TOPICS, assess_demand, google_news_rss_for_query, google_trends_explore_url
from aoip.intelligence.editorial import assess_conversation
from aoip.models import Conversation, DemandSignal, ScanRun, SocialSignal, SourceConfig


SOCIAL_KINDS = {"social_reddit_rss", "social_youtube_discovery", "social_youtube_channel_rss"}
DEMAND_KINDS = {"demand_google_news_rss"}


def run_social_scan(settings: AppSettings) -> int:
    ai = AIClient(settings)
    found = 0
    with session_scope() as session:
        sources = session.query(SourceConfig).filter(SourceConfig.is_active.is_(True), SourceConfig.kind.in_(list(SOCIAL_KINDS))).all()
        for source in sources:
            platform = _platform_for_source(source.kind)
            for item in fetch_rss(source.url, source.name, limit=settings.scan_depth):
                if not item.url:
                    continue
                exists = session.query(SocialSignal).filter(SocialSignal.url == item.url).first()
                if exists:
                    continue
                assessment = assess_conversation(item.title, item.summary, settings.countries, settings.industries, ai)
                signal = SocialSignal(
                    platform=platform,
                    title=item.title,
                    url=item.url,
                    source=source.name,
                    author=item.author,
                    published_at=item.published_at,
                    summary=assessment.summary,
                    country=assessment.country,
                    industry=assessment.industry,
                    signal_type="video" if platform == "youtube" else "post",
                    opportunity_score=assessment.opportunity_score,
                    relationship_score=assessment.relationship_score,
                    authority_score=assessment.authority_score,
                    suggested_reply=assessment.suggested_comment,
                    follow_up_question=assessment.follow_up_question,
                )
                session.add(signal)
                if not session.query(Conversation).filter(Conversation.url == item.url).first():
                    session.add(
                        Conversation(
                            title=item.title,
                            url=item.url,
                            source=f"{platform}: {source.name}",
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
        session.add(ScanRun(name=f"Social scan {datetime.now():%Y-%m-%d %H:%M}", items_found=found, notes="Reddit and YouTube discovery feeds"))
    return found


def run_demand_scan(settings: AppSettings) -> int:
    found = 0
    with session_scope() as session:
        source_rows = session.query(SourceConfig).filter(SourceConfig.is_active.is_(True), SourceConfig.kind.in_(list(DEMAND_KINDS))).all()
        source_queries = [(source.name, source.url, _topic_from_source_name(source.name), "") for source in source_rows]
        topic_queries = [(topic, google_news_rss_for_query(query), topic, industry) for topic, query, industry in DEMAND_TOPICS]

        for source_name, url, topic, industry in source_queries + topic_queries:
            items = fetch_rss(url, source_name, limit=min(settings.scan_depth, 20))
            if not items:
                continue
            query = topic
            evidence_url = google_trends_explore_url(query)
            exists = session.query(DemandSignal).filter(DemandSignal.topic == topic, DemandSignal.evidence_url == evidence_url).first()
            if exists:
                exists.evidence_count = max(exists.evidence_count, len(items))
                continue
            assessment = assess_demand(topic, query, industry, items)
            session.add(
                DemandSignal(
                    topic=topic,
                    query=query,
                    country="Africa",
                    industry=industry,
                    source=source_name,
                    evidence_url=evidence_url,
                    evidence_count=len(items),
                    demand_score=assessment.demand_score,
                    authority_gap_score=assessment.authority_gap_score,
                    recommended_content=assessment.recommended_content,
                    suggested_title=assessment.suggested_title,
                    suggested_outline=assessment.suggested_outline,
                )
            )
            found += 1
        session.add(ScanRun(name=f"Demand scan {datetime.now():%Y-%m-%d %H:%M}", items_found=found, notes="Google News RSS demand evidence and Google Trends links"))
    return found


def _platform_for_source(kind: str) -> str:
    if "youtube" in kind:
        return "youtube"
    if "reddit" in kind:
        return "reddit"
    return "social"


def _topic_from_source_name(name: str) -> str:
    return name.replace("Demand - ", "").strip()
