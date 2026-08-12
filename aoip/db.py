from __future__ import annotations

import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from aoip.config import BACKUP_DIR, DATA_DIR, ensure_directories
from aoip.models import Base, SourceConfig


DB_PATH = DATA_DIR / "aoip.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(DATABASE_URL, future=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def init_db() -> None:
    ensure_directories()
    Base.metadata.create_all(engine)
    seed_defaults()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def seed_defaults() -> None:
    defaults = [
        ("African Development Bank - News & Events", "rss", "https://www.afdb.org/en/news-and-events/rss.xml", "Official AfDB RSS feed for development finance, projects, procurement, and policy signals."),
        ("African Business", "rss", "https://african.business/feed", "African business, finance, politics, technology, energy, and market intelligence."),
        ("Business Post Nigeria", "rss", "https://businesspost.ng/feed", "Nigeria business, finance, markets, regulation, banking, and corporate news."),
        ("Central Bank of Nigeria - Circulars", "rss", "https://www.cbn.gov.ng/RSS/CircularsRSS.html", "Official CBN circulars feed for payments, banking, FX, and financial regulation."),
        ("Central Bank of Nigeria - Publications", "rss", "https://www.cbn.gov.ng/RSS/PublicationsRSS.html", "Official CBN publications feed for economic reports, rates, and MPC material."),
        ("Disrupt Africa", "rss", "https://disruptafrica.com/feed/", "Africa startup, funding, founder, ecosystem, investment, and venture news."),
        ("How We Made It In Africa", "rss", "https://www.howwemadeitinafrica.com/feed/", "African entrepreneurs, market opportunities, business models, and operator interviews."),
        ("IT News Africa", "rss", "https://www.itnewsafrica.com/feed/", "Africa technology, telecoms, enterprise IT, cybersecurity, and digital transformation."),
        ("TechCabal", "rss", "https://techcabal.com/feed/", "African technology, startups, fintech, policy, funding, and digital economy coverage."),
        ("Techpoint Africa", "rss", "https://techpoint.africa/feed/", "African startup, technology, telecoms, product, and funding coverage."),
        ("Ventures Africa", "rss", "https://venturesafrica.com/feed/", "African business, entrepreneurship, economy, innovation, and investment coverage."),
        ("World Bank Africa", "rss", "https://blogs.worldbank.org/en/africacan/rss.xml", "World Bank Africa development economics, policy, infrastructure, and poverty analysis."),
        ("Google News - Africa AI Infrastructure", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20AI%20infrastructure%20startups%20funding", "Google News RSS monitor for AI infrastructure, compute, data centers, and startup funding."),
        ("Google News - Africa Climate Finance", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20climate%20finance%20investment%20startups", "Google News RSS monitor for climate finance, project bankability, carbon markets, and green investment."),
        ("Google News - Africa Digital Economy Policy", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20digital%20economy%20policy%20regulation", "Google News RSS monitor for policy, regulation, digital public infrastructure, and market rules."),
        ("Google News - Africa Energy Infrastructure", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20energy%20infrastructure%20investment%20technology", "Google News RSS monitor for power, grids, renewables, infrastructure, and project finance."),
        ("Google News - Africa Fintech Regulation", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20fintech%20payments%20regulation%20central%20bank", "Google News RSS monitor for fintech, payments, central banks, licensing, and compliance."),
        ("Google News - Africa Startup Funding", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20startup%20funding%20venture%20capital", "Google News RSS monitor for startup funding, venture capital, exits, and ecosystem shifts."),
        ("Google News - Africa Trade AfCFTA", "google_news_rss", "https://news.google.com/rss/search?q=Africa%20trade%20AfCFTA%20manufacturing%20logistics", "Google News RSS monitor for trade, AfCFTA, manufacturing, logistics, and market access."),
        ("Google News - African Markets Expansion", "google_news_rss", "https://news.google.com/rss/search?q=companies%20expanding%20into%20Africa%20market%20entry", "Google News RSS monitor for companies entering or expanding across African markets."),
        ("Reddit - Africa Startup Funding", "social_reddit_rss", "https://www.reddit.com/search.rss?q=Africa%20startup%20funding%20venture%20capital&sort=new", "Public Reddit search RSS for Africa startup funding and VC conversations."),
        ("Reddit - African Entrepreneurs", "social_reddit_rss", "https://www.reddit.com/search.rss?q=African%20entrepreneurs%20startup%20business&sort=new", "Public Reddit search RSS for founder and entrepreneur questions related to Africa."),
        ("Reddit - Nigeria Fintech", "social_reddit_rss", "https://www.reddit.com/search.rss?q=Nigeria%20fintech%20payments%20startup&sort=new", "Public Reddit search RSS for fintech, payments, and operator questions in Nigeria."),
        ("Reddit - Africa AI", "social_reddit_rss", "https://www.reddit.com/search.rss?q=Africa%20AI%20startup%20technology&sort=new", "Public Reddit search RSS for AI, technology, and Africa startup discussions."),
        ("Reddit - Climate Finance Africa", "social_reddit_rss", "https://www.reddit.com/search.rss?q=Africa%20climate%20finance%20carbon%20markets&sort=new", "Public Reddit search RSS for climate finance, green investment, and carbon-market conversations."),
        ("YouTube Discovery - Africa Startup Funding", "social_youtube_discovery", "https://news.google.com/rss/search?q=site%3Ayoutube.com%20Africa%20startup%20funding%20venture%20capital", "Google News RSS discovery for YouTube videos on Africa startup funding and VC."),
        ("YouTube Discovery - Africa AI Technology", "social_youtube_discovery", "https://news.google.com/rss/search?q=site%3Ayoutube.com%20Africa%20AI%20technology%20startups", "Google News RSS discovery for YouTube videos on Africa AI and technology."),
        ("YouTube Discovery - Africa Business Podcasts", "social_youtube_discovery", "https://news.google.com/rss/search?q=site%3Ayoutube.com%20Africa%20business%20podcast%20entrepreneurship", "Google News RSS discovery for YouTube business podcasts and interviews."),
        ("Demand - What Africa Is Searching", "demand_google_news_rss", "https://news.google.com/rss/search?q=Africa%20how%20to%20startup%20funding%20business%20opportunity", "Demand monitor for how/what/why questions around Africa business opportunities."),
        ("Demand - Startup Grants Africa", "demand_google_news_rss", "https://news.google.com/rss/search?q=startup%20grants%20Africa%20funding%20entrepreneurs", "Demand monitor for grants, startup finance, and founder education opportunities."),
        ("Demand - AfCFTA Opportunities", "demand_google_news_rss", "https://news.google.com/rss/search?q=AfCFTA%20opportunities%20small%20business%20trade%20Africa", "Demand monitor for trade education, AfCFTA opportunities, and market access questions."),
        ("Demand - AI Business Africa", "demand_google_news_rss", "https://news.google.com/rss/search?q=AI%20business%20opportunities%20Africa%20startups", "Demand monitor for AI business, adoption, education, and startup opportunity searches."),
        ("Demand - Climate Finance Africa", "demand_google_news_rss", "https://news.google.com/rss/search?q=climate%20finance%20Africa%20how%20to%20invest%20projects", "Demand monitor for climate finance education, bankable projects, and green investment."),
    ]
    with SessionLocal() as session:
        for name, kind, url, notes in defaults:
            exists = session.query(SourceConfig).filter(SourceConfig.name == name).first()
            if not exists:
                session.add(SourceConfig(name=name, kind=kind, url=url, notes=notes))
            elif not exists.notes:
                exists.notes = notes
        session.commit()


def backup_database() -> Path | None:
    ensure_directories()
    if not DB_PATH.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"aoip-{stamp}.sqlite3"
    shutil.copy2(DB_PATH, target)
    return target
