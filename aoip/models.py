from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class SourceConfig(Base, TimestampMixin):
    __tablename__ = "source_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    kind: Mapped[str] = mapped_column(String(80))
    url: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, default="")


class SearchQuery(Base, TimestampMixin):
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    last_run_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(120), default="manual")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    author: Mapped[str] = mapped_column(String(200), default="")
    summary: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text, default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    pillar: Mapped[str] = mapped_column(String(120), default="")
    people: Mapped[str] = mapped_column(Text, default="")
    companies: Mapped[str] = mapped_column(Text, default="")
    engagement: Mapped[int] = mapped_column(Integer, default=0)
    opportunity_score: Mapped[float] = mapped_column(Float, default=0.0)
    relationship_score: Mapped[float] = mapped_column(Float, default=0.0)
    authority_score: Mapped[float] = mapped_column(Float, default=0.0)
    recommended_action: Mapped[str] = mapped_column(String(120), default="review")
    suggested_comment: Mapped[str] = mapped_column(Text, default="")
    follow_up_question: Mapped[str] = mapped_column(Text, default="")
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)


class KnowledgeItem(Base, TimestampMixin):
    __tablename__ = "knowledge_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(80), default="note")
    body: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(Text, default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    vector_id: Mapped[str] = mapped_column(String(200), default="")


class Person(Base, TimestampMixin):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    role: Mapped[str] = mapped_column(String(200), default="")
    organization: Mapped[str] = mapped_column(String(200), default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    topics: Mapped[str] = mapped_column(Text, default="")
    influence_score: Mapped[float] = mapped_column(Float, default=0.0)
    relationship_score: Mapped[float] = mapped_column(Float, default=0.0)
    next_action: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    stage: Mapped[str] = mapped_column(String(120), default="")
    signals: Mapped[str] = mapped_column(Text, default="")
    partnership_score: Mapped[float] = mapped_column(Float, default=0.0)
    sponsorship_score: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")


class TrendSignal(Base, TimestampMixin):
    __tablename__ = "trend_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    signal_type: Mapped[str] = mapped_column(String(120), default="conversation")
    strength: Mapped[float] = mapped_column(Float, default=0.0)
    direction: Mapped[str] = mapped_column(String(40), default="stable")
    evidence: Mapped[str] = mapped_column(Text, default="")


class SocialSignal(Base, TimestampMixin):
    __tablename__ = "social_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    platform: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(200), default="")
    author: Mapped[str] = mapped_column(String(200), default="")
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    country: Mapped[str] = mapped_column(String(120), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    signal_type: Mapped[str] = mapped_column(String(80), default="post")
    opportunity_score: Mapped[float] = mapped_column(Float, default=0.0)
    relationship_score: Mapped[float] = mapped_column(Float, default=0.0)
    authority_score: Mapped[float] = mapped_column(Float, default=0.0)
    suggested_reply: Mapped[str] = mapped_column(Text, default="")
    follow_up_question: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="new")


class DemandSignal(Base, TimestampMixin):
    __tablename__ = "demand_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic: Mapped[str] = mapped_column(String(200))
    query: Mapped[str] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(120), default="Africa")
    industry: Mapped[str] = mapped_column(String(120), default="")
    source: Mapped[str] = mapped_column(String(120), default="google_news_rss")
    evidence_url: Mapped[str] = mapped_column(Text, default="")
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    demand_score: Mapped[float] = mapped_column(Float, default=0.0)
    authority_gap_score: Mapped[float] = mapped_column(Float, default=0.0)
    recommended_content: Mapped[str] = mapped_column(Text, default="")
    suggested_title: Mapped[str] = mapped_column(Text, default="")
    suggested_outline: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="new")


class OpportunityReport(Base, TimestampMixin):
    __tablename__ = "opportunity_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(String(120))
    topic: Mapped[str] = mapped_column(String(200), default="")
    audience: Mapped[str] = mapped_column(Text, default="")
    why_now: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[str] = mapped_column(Text, default="")
    outline: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(80), default="medium")
    authority_impact: Mapped[float] = mapped_column(Float, default=0.0)
    content_length: Mapped[str] = mapped_column(String(80), default="1200-1800 words")


class EditorialCalendarItem(Base, TimestampMixin):
    __tablename__ = "editorial_calendar_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    publish_date: Mapped[datetime] = mapped_column(DateTime)
    channel: Mapped[str] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(Text)
    format: Mapped[str] = mapped_column(String(120))
    priority: Mapped[float] = mapped_column(Float, default=0.0)
    rationale: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="idea")


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    report_type: Mapped[str] = mapped_column(String(120))
    body_markdown: Mapped[str] = mapped_column(Text)
    export_path: Mapped[str] = mapped_column(Text, default="")


class ScanRun(Base, TimestampMixin):
    __tablename__ = "scan_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(80), default="completed")
    items_found: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
