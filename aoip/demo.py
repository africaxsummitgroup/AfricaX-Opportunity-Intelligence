from __future__ import annotations

from datetime import datetime, timedelta

from aoip.db import session_scope
from aoip.models import Company, Conversation, KnowledgeItem, Person


def seed_demo_data() -> None:
    with session_scope() as session:
        demo_urls = {
            "African AI infrastructure startups are becoming a regional investment theme": "https://news.google.com/search?q=African%20AI%20infrastructure%20startups%20funding",
            "New payments regulation is shifting fintech strategy in Nigeria": "https://news.google.com/search?q=Nigeria%20payments%20regulation%20fintech",
            "Climate finance conversations are moving from pledges to bankable projects": "https://news.google.com/search?q=Africa%20climate%20finance%20bankable%20projects",
            "Manufacturing clusters are getting renewed attention across West Africa": "https://news.google.com/search?q=West%20Africa%20manufacturing%20clusters%20investment",
        }
        for title, url in demo_urls.items():
            existing = session.query(Conversation).filter(Conversation.title == title).first()
            if existing and not existing.url:
                existing.url = url

        if session.query(Conversation).filter(Conversation.source == "demo intelligence").count() >= 4:
            return

        session.add_all(
            [
                Conversation(
                    title="African AI infrastructure startups are becoming a regional investment theme",
                    source="demo intelligence",
                    url="https://news.google.com/search?q=African%20AI%20infrastructure%20startups%20funding",
                    published_at=datetime.now() - timedelta(hours=6),
                    summary="Investors and operators are discussing data centers, model deployment, cloud credits, and local AI infrastructure for African markets.",
                    content="What does Africa need to make AI infrastructure practical for startups? Funding, compute access, data governance and talent all appear repeatedly.",
                    country="Africa",
                    industry="AI",
                    pillar="Innovation",
                    people="founders, investors",
                    companies="AI infrastructure startups",
                    engagement=86,
                    opportunity_score=88,
                    relationship_score=72,
                    authority_score=84,
                    recommended_action="publish",
                    suggested_comment="The infrastructure layer is becoming as important as applications. AfricaX could map the practical bottlenecks: compute, data access, deployment costs, and policy.",
                    follow_up_question="Which AI infrastructure constraints are most urgent for African founders in the next 12 months?",
                ),
                Conversation(
                    title="New payments regulation is shifting fintech strategy in Nigeria",
                    source="demo intelligence",
                    url="https://news.google.com/search?q=Nigeria%20payments%20regulation%20fintech",
                    published_at=datetime.now() - timedelta(hours=13),
                    summary="Operators are asking how new compliance expectations affect wallets, cross-border payments, agent networks, and embedded finance.",
                    content="Why are fintech teams changing product roadmaps after regulatory updates? The answer is not just compliance; it is market positioning.",
                    country="Nigeria",
                    industry="fintech",
                    pillar="Economic Development",
                    engagement=64,
                    opportunity_score=79,
                    relationship_score=58,
                    authority_score=82,
                    recommended_action="investigate",
                    suggested_comment="A useful public analysis would separate the regulatory facts from the strategic implications for founders, banks, and payment infrastructure providers.",
                    follow_up_question="Which part of the new compliance burden changes the economics of Nigerian fintech the most?",
                ),
                Conversation(
                    title="Climate finance conversations are moving from pledges to bankable projects",
                    source="demo intelligence",
                    url="https://news.google.com/search?q=Africa%20climate%20finance%20bankable%20projects",
                    published_at=datetime.now() - timedelta(days=1),
                    summary="Development finance institutions and project developers are discussing blended finance, project preparation, and local execution capacity.",
                    content="How can African climate projects become more bankable? Repeated answers point to project preparation, risk guarantees, and local operating partners.",
                    country="Kenya",
                    industry="climate",
                    pillar="Investment",
                    engagement=51,
                    opportunity_score=74,
                    relationship_score=68,
                    authority_score=78,
                    recommended_action="publish",
                    suggested_comment="The missing layer is often project preparation. AfricaX could help readers understand what turns climate ambition into financeable projects.",
                    follow_up_question="What makes a climate project bankable in African markets before institutional capital arrives?",
                ),
                Conversation(
                    title="Manufacturing clusters are getting renewed attention across West Africa",
                    source="demo intelligence",
                    url="https://news.google.com/search?q=West%20Africa%20manufacturing%20clusters%20investment",
                    published_at=datetime.now() - timedelta(days=2),
                    summary="Trade, power, logistics, and special economic zones are appearing together in policy and founder discussions.",
                    content="Which manufacturing categories can scale regionally from West Africa? Apparel, food processing, assembly and packaging are frequently mentioned.",
                    country="Ghana",
                    industry="manufacturing",
                    pillar="Business Opportunity",
                    engagement=42,
                    opportunity_score=69,
                    relationship_score=45,
                    authority_score=70,
                    recommended_action="investigate",
                    suggested_comment="The conversation becomes more useful when manufacturing is broken into specific categories, infrastructure needs, and buyer demand.",
                    follow_up_question="Which manufacturing niches have the strongest combination of local demand and export potential?",
                ),
            ]
        )
        session.add_all(
            [
                Person(
                    name="Demo Founder",
                    role="Founder",
                    organization="AI infrastructure startup",
                    country="Nigeria",
                    topics="AI, cloud, infrastructure",
                    influence_score=72,
                    relationship_score=66,
                    next_action="Invite for a short expert interview on African AI infrastructure.",
                ),
                Person(
                    name="Demo Investor",
                    role="Investor",
                    organization="Pan-African venture fund",
                    country="Kenya",
                    topics="fintech, climate, AI",
                    influence_score=81,
                    relationship_score=58,
                    next_action="Engage with a thoughtful public comment, then save for future panel.",
                ),
            ]
        )
        session.add_all(
            [
                Company(
                    name="Demo Compute Africa",
                    country="Nigeria",
                    industry="AI",
                    stage="Seed",
                    signals="Hiring ML infrastructure engineers; discussing local deployment costs.",
                    partnership_score=76,
                    sponsorship_score=61,
                    notes="Potential research partner for AI infrastructure report.",
                ),
                Company(
                    name="Demo Climate Capital",
                    country="Kenya",
                    industry="climate",
                    stage="Growth",
                    signals="Publishing analysis on bankable climate projects.",
                    partnership_score=69,
                    sponsorship_score=74,
                    notes="Potential sponsor for climate finance briefing.",
                ),
            ]
        )
        session.add(
            KnowledgeItem(
                title="AfricaX editorial thesis",
                kind="framework",
                body="AfricaX should win authority by explaining business opportunity with evidence, context, and useful frameworks instead of surface-level news reactions.",
                tags="strategy, authority, editorial",
                country="Africa",
                industry="business opportunity",
            )
        )
