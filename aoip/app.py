from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st

from aoip.ai import AIClient
from aoip.automation import run_daily_scan
from aoip.config import AppSettings, load_settings, save_settings
from aoip.connectors.rss import fetch_rss
from aoip.db import backup_database, init_db, session_scope
from aoip.demo import seed_demo_data
from aoip.intelligence.editorial import assess_conversation
from aoip.intelligence.gaps import detect_content_gaps
from aoip.intelligence.relationships import recommended_relationship_action
from aoip.intelligence.trends import trend_snapshot
from aoip.models import (
    Company,
    Conversation,
    EditorialCalendarItem,
    KnowledgeItem,
    OpportunityReport,
    Person,
    Report,
    SearchQuery,
    SourceConfig,
)
from aoip.reports.generator import content_gap_report, daily_brief, export_conversations_csv, export_markdown
from aoip.search.operators import DEFAULT_SITES, generate_search_operators
from aoip.vector_store import VectorStore


st.set_page_config(page_title="AOIP", page_icon="AX", layout="wide", initial_sidebar_state="expanded")


def main() -> None:
    init_db()
    settings = load_settings()
    if settings.offline_demo_mode:
        seed_demo_data()
    inject_css()

    st.sidebar.title("AOIP")
    st.sidebar.caption("AfricaX Opportunity Intelligence Platform")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Daily Scan",
            "Conversations",
            "Search Operators",
            "Content Gaps",
            "Trend Intelligence",
            "Relationship Intelligence",
            "Company Intelligence",
            "Second Brain",
            "Editorial Calendar",
            "Reports",
            "Strategic Roadmap",
            "Settings",
        ],
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    st.sidebar.metric("AI Mode", "Live" if AIClient(settings).is_live else "Offline demo")
    st.sidebar.metric("Vector DB", "Chroma" if VectorStore(AIClient(settings)).is_chroma_enabled else "Memory fallback")

    if page == "Dashboard":
        render_dashboard()
    elif page == "Daily Scan":
        render_daily_scan(settings)
    elif page == "Conversations":
        render_conversations()
    elif page == "Search Operators":
        render_search_operators(settings)
    elif page == "Content Gaps":
        render_content_gaps()
    elif page == "Trend Intelligence":
        render_trends()
    elif page == "Relationship Intelligence":
        render_relationships()
    elif page == "Company Intelligence":
        render_companies()
    elif page == "Second Brain":
        render_second_brain(settings)
    elif page == "Editorial Calendar":
        render_calendar()
    elif page == "Reports":
        render_reports()
    elif page == "Strategic Roadmap":
        render_strategic_roadmap()
    elif page == "Settings":
        render_settings(settings)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.5rem; }
        div[data-testid="stMetric"] {
            background: #151B23;
            border: 1px solid #263241;
            border-radius: 8px;
            padding: 14px 16px;
        }
        .aoip-card {
            background: #151B23;
            border: 1px solid #263241;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0 14px 0;
        }
        .muted { color: #9CA3AF; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    st.title("AfricaX Opportunity Intelligence")
    st.caption("The highest-leverage intelligence cockpit for AfricaX editorial, research, relationship, and authority decisions.")
    conversations = load_conversations()
    people = load_people()
    companies = load_companies()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Signals", len(conversations))
    c2.metric("Avg Opportunity", f"{avg([c.opportunity_score for c in conversations]):.0f}")
    c3.metric("Tracked People", len(people))
    c4.metric("Tracked Companies", len(companies))

    top = sorted(conversations, key=lambda item: item.opportunity_score, reverse=True)[:1]
    if top:
        best = top[0]
        st.subheader("Highest-Leverage Move")
        st.markdown(
            f"""
            <div class="aoip-card">
            <h3>{best.title}</h3>
            <p class="muted">{best.country} | {best.industry} | {best.pillar}</p>
            <p>{best.summary}</p>
            <strong>Recommended action:</strong> {best.recommended_action}<br/>
            <strong>Follow-up question:</strong> {best.follow_up_question}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if best.url:
            st.link_button("Open original signal", best.url)

    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Priority Signals")
        show_conversation_table(conversations)
    with right:
        st.subheader("Opportunity by Industry")
        rows = [{"industry": c.industry or "General", "score": c.opportunity_score} for c in conversations]
        if rows:
            df = pd.DataFrame(rows).groupby("industry", as_index=False)["score"].mean()
            st.plotly_chart(px.bar(df, x="score", y="industry", orientation="h", color="score"), use_container_width=True)


def render_daily_scan(settings: AppSettings) -> None:
    st.title("Daily Scan")
    st.caption("Run permitted RSS and API-based collection, then classify each signal for opportunity, authority, and relationship value.")
    if st.button("Run Daily Intelligence Scan", type="primary", help="Fetches active RSS and Google News RSS sources."):
        with st.spinner("Scanning active sources and assessing new signals..."):
            count = run_daily_scan(settings)
        st.success(f"Scan complete. Added {count} new signals.")

    with session_scope() as session:
        sources = session.query(SourceConfig).order_by(SourceConfig.name).all()
    st.subheader("Active Sources")
    if sources:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Name": s.name,
                        "Kind": s.kind,
                        "Open": s.url,
                        "Active": s.is_active,
                        "Notes": s.notes,
                    }
                    for s in sources
                ]
            ),
            use_container_width=True,
            column_config=link_column_config(),
        )
    if st.button("Check Source Health", help="Fetches a few items from each active feed and shows whether links are being returned."):
        rows = []
        with st.spinner("Checking active RSS and Google News RSS sources..."):
            for source in sources:
                if source.kind not in {"rss", "google_news_rss"} or not source.is_active:
                    continue
                items = fetch_rss(source.url, source.name, limit=3)
                rows.append(
                    {
                        "Source": source.name,
                        "Kind": source.kind,
                        "Items Found": len(items),
                        "Sample Title": items[0].title if items else "",
                        "Open": items[0].url if items else source.url,
                    }
                )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, column_config=link_column_config())

    with st.expander("Add Source"):
        with st.form("add_source"):
            name = st.text_input("Source name")
            kind = st.selectbox("Source type", ["rss", "google_news_rss", "official_api", "manual"])
            url = st.text_input("Feed or API URL")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save Source")
        if submitted and name:
            with session_scope() as session:
                session.add(SourceConfig(name=name, kind=kind, url=url, notes=notes))
            st.success("Source saved.")
            st.rerun()


def render_conversations() -> None:
    st.title("Conversation Intelligence")
    conversations = load_conversations()
    query = st.text_input("Filter signals", placeholder="Try fintech, Nigeria, AI, policy, investor...")
    action = st.multiselect("Recommended action", sorted({c.recommended_action for c in conversations}))
    filtered = [
        c
        for c in conversations
        if (not query or query.lower() in f"{c.title} {c.summary} {c.country} {c.industry}".lower())
        and (not action or c.recommended_action in action)
    ]
    show_conversation_table(filtered)

    st.subheader("Add Manual Signal")
    with st.form("manual_signal"):
        title = st.text_input("Title")
        content = st.text_area("What is being discussed?")
        url = st.text_input("Original URL", placeholder="https://...")
        country = st.text_input("Country", value="Africa")
        industry = st.text_input("Industry")
        source = st.text_input("Source", value="manual")
        submitted = st.form_submit_button("Analyze and Save")
    if submitted and title:
        settings = load_settings()
        assessment = assess_conversation(title, content, settings.countries, settings.industries, AIClient(settings))
        with session_scope() as session:
            session.add(
                Conversation(
                    title=title,
                    url=url,
                    content=content,
                    source=source,
                    country=country or assessment.country,
                    industry=industry or assessment.industry,
                    pillar=assessment.pillar,
                    summary=assessment.summary,
                    opportunity_score=assessment.opportunity_score,
                    relationship_score=assessment.relationship_score,
                    authority_score=assessment.authority_score,
                    recommended_action=assessment.recommended_action,
                    suggested_comment=assessment.suggested_comment,
                    follow_up_question=assessment.follow_up_question,
                )
            )
        st.success("Signal analyzed and saved.")
        st.rerun()


def render_search_operators(settings: AppSettings) -> None:
    st.title("Search Operator Factory")
    st.caption("Generate thousands of focused Google operator queries without brittle scraping.")
    countries = st.text_area("Countries", value=", ".join(settings.countries))
    industries = st.text_area("Industries", value=", ".join(settings.industries))
    sites = st.multiselect("Sites", DEFAULT_SITES, default=DEFAULT_SITES)
    limit = st.slider("Query limit", 50, 3000, 500, step=50)
    queries = generate_search_operators(split_csv(countries), split_csv(industries), sites=sites, limit=limit)
    st.metric("Generated Queries", len(queries))
    df = pd.DataFrame([q.__dict__ for q in queries])
    st.dataframe(df, use_container_width=True, height=420)
    if st.button("Save Queries"):
        with session_scope() as session:
            for q in queries:
                session.add(SearchQuery(query=q.query, source=q.site, country=q.country, industry=q.industry))
        st.success(f"Saved {len(queries)} queries.")


def render_content_gaps() -> None:
    st.title("Content Gap Detection")
    conversations = load_conversations()
    gaps = detect_content_gaps(conversations)
    if st.button("Generate Content Opportunity Reports", type="primary"):
        with session_scope() as session:
            for gap in gaps:
                session.add(
                    OpportunityReport(
                        title=gap.suggested_title,
                        report_type="content_gap",
                        topic=gap.topic,
                        audience=gap.audience,
                        why_now=f"Demand score {gap.demand_score:.0f}. {gap.evidence}",
                        evidence=gap.evidence,
                        outline=gap.outline,
                        difficulty=gap.difficulty,
                        authority_impact=gap.authority_impact,
                    )
                )
        st.success("Content opportunity reports generated.")
    for gap in gaps:
        st.markdown(f"### {gap.suggested_title}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Demand", f"{gap.demand_score:.0f}")
        c2.metric("Authority Impact", f"{gap.authority_impact:.0f}")
        c3.metric("Difficulty", gap.difficulty)
        st.write(gap.evidence)
        st.code(gap.outline)
        matched = matching_conversations_for_topic(conversations, gap.topic)
        if matched:
            with st.expander("Evidence signals"):
                show_conversation_table(matched, height=240)


def render_trends() -> None:
    st.title("Trend Intelligence")
    conversations = load_conversations()
    rows = trend_snapshot(conversations)
    if not rows:
        st.info("No trend signals yet.")
        return
    df = pd.DataFrame(rows)
    st.plotly_chart(px.scatter(df, x="signals", y="strength", size="strength", color="direction", hover_name="topic"), use_container_width=True)
    st.dataframe(df, use_container_width=True)
    selected_topic = st.selectbox("Show evidence for topic", [str(row["topic"]) for row in rows])
    show_conversation_table(matching_conversations_for_topic(conversations, selected_topic), height=320)


def render_relationships() -> None:
    st.title("Relationship Intelligence")
    people = load_people()
    if people:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Name": p.name,
                        "Role": p.role,
                        "Organization": p.organization,
                        "Country": p.country,
                        "Topics": p.topics,
                        "Influence": p.influence_score,
                        "Relationship": p.relationship_score,
                        "Next Action": p.next_action,
                    }
                    for p in people
                ]
            ),
            use_container_width=True,
        )
    st.subheader("Relationship Actions From Signals")
    for item in sorted(load_conversations(), key=lambda c: c.relationship_score, reverse=True)[:8]:
        st.markdown(f"**{item.title}**")
        st.write(recommended_relationship_action(item))
        st.caption(item.suggested_comment)
        if item.url:
            st.link_button("Open source", item.url, key=f"relationship-source-{item.id}")


def render_companies() -> None:
    st.title("Company Intelligence")
    companies = load_companies()
    if not companies:
        st.info("No companies tracked yet.")
        return
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Company": c.name,
                    "Country": c.country,
                    "Industry": c.industry,
                    "Stage": c.stage,
                    "Partnership": c.partnership_score,
                    "Sponsorship": c.sponsorship_score,
                    "Signals": c.signals,
                }
                for c in companies
            ]
        ),
        use_container_width=True,
    )


def render_second_brain(settings: AppSettings) -> None:
    st.title("Second Brain")
    ai = AIClient(settings)
    store = VectorStore(ai)
    st.caption("Store AfricaX articles, notes, frameworks, quotes, meeting notes, reports, and ideas. Search semantically across everything.")

    with st.form("knowledge_form"):
        title = st.text_input("Title")
        kind = st.selectbox("Type", ["article", "linkedin_post", "research_report", "framework", "idea", "draft", "book", "paper", "quote", "personal_note", "meeting_note"])
        body = st.text_area("Content", height=180)
        tags = st.text_input("Tags")
        submitted = st.form_submit_button("Save to Knowledge Base")
    if submitted and title and body:
        with session_scope() as session:
            item = KnowledgeItem(title=title, kind=kind, body=body, tags=tags)
            session.add(item)
            session.flush()
            vector_id = f"knowledge-{item.id}"
            item.vector_id = vector_id
            store.upsert(vector_id, f"{title}\n{body}", {"title": title, "kind": kind, "tags": tags})
        st.success("Saved and embedded.")
        st.rerun()

    query = st.text_input("Semantic search")
    if query:
        for hit in store.search(query, n_results=8):
            st.markdown(f"**{hit.metadata.get('title', hit.id)}**")
            st.caption(f"{hit.metadata.get('kind', 'item')} | distance {hit.distance:.3f}")
            st.write(hit.text[:600])

    with session_scope() as session:
        items = session.query(KnowledgeItem).order_by(KnowledgeItem.updated_at.desc()).limit(50).all()
    st.subheader("Recent Knowledge")
    st.dataframe(pd.DataFrame([{"Title": i.title, "Type": i.kind, "Tags": i.tags, "Updated": i.updated_at} for i in items]), use_container_width=True)


def render_calendar() -> None:
    st.title("Editorial Calendar AI")
    conversations = load_conversations()
    if st.button("Generate Next 7 Days", type="primary"):
        top = sorted(conversations, key=lambda item: item.opportunity_score + item.authority_score, reverse=True)[:7]
        formats = ["LinkedIn post", "Substack essay", "Research brief", "Founder interview", "Carousel", "Panel discussion", "Newsletter"]
        with session_scope() as session:
            for index, item in enumerate(top):
                session.add(
                    EditorialCalendarItem(
                        publish_date=datetime.now() + timedelta(days=index + 1),
                        channel=formats[index % len(formats)],
                        title=f"AfricaX perspective: {item.title}",
                        format=formats[index % len(formats)],
                        priority=item.opportunity_score,
                        rationale=f"Strong opportunity and authority signal in {item.industry} for {item.country}.",
                    )
                )
        st.success("Editorial calendar generated.")
    with session_scope() as session:
        items = session.query(EditorialCalendarItem).order_by(EditorialCalendarItem.publish_date).all()
    if items:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Date": i.publish_date.date(),
                        "Channel": i.channel,
                        "Format": i.format,
                        "Title": i.title,
                        "Priority": i.priority,
                        "Status": i.status,
                        "Rationale": i.rationale,
                    }
                    for i in items
                ]
            ),
            use_container_width=True,
        )


def render_reports() -> None:
    st.title("Reports")
    conversations = load_conversations()
    with session_scope() as session:
        opportunity_reports = session.query(OpportunityReport).all()
    report_type = st.selectbox("Report type", ["Daily Intelligence Brief", "Content Gap Report", "Conversation CSV Export"])
    if st.button("Generate Export", type="primary"):
        if report_type == "Daily Intelligence Brief":
            markdown = daily_brief(conversations)
            path = export_markdown("daily-intelligence-brief", markdown)
            save_report("Daily Intelligence Brief", "daily", markdown, path)
            st.success(f"Exported Markdown: {path}")
            st.markdown(markdown)
        elif report_type == "Content Gap Report":
            markdown = content_gap_report(opportunity_reports)
            path = export_markdown("content-gap-report", markdown)
            save_report("Content Gap Report", "content_gap", markdown, path)
            st.success(f"Exported Markdown: {path}")
            st.markdown(markdown)
        else:
            path = export_conversations_csv(conversations)
            st.success(f"Exported CSV: {path}")

    with session_scope() as session:
        reports = session.query(Report).order_by(Report.created_at.desc()).limit(20).all()
    if reports:
        st.subheader("Recent Reports")
        st.dataframe(pd.DataFrame([{"Title": r.title, "Type": r.report_type, "Path": r.export_path, "Created": r.created_at} for r in reports]), use_container_width=True)


def render_strategic_roadmap() -> None:
    st.title("Strategic Roadmap")
    st.caption("Product and intelligence features that would make AOIP more valuable as AfricaX's private strategy engine.")
    recommendations = [
        {
            "Feature": "Evidence graph",
            "Priority": "High",
            "Why it matters": "Connect people, companies, countries, industries, sources, and reports so AfricaX can see why a recommendation exists.",
            "Suggested implementation": "Create relationship tables and a graph view linking signals to entities and actions.",
        },
        {
            "Feature": "Saved intelligence briefs by topic",
            "Priority": "High",
            "Why it matters": "AfricaX needs recurring briefs for AI, fintech, climate, policy, funding, and market entry.",
            "Suggested implementation": "Let users subscribe to topic/country watchlists and auto-generate weekly briefs.",
        },
        {
            "Feature": "Source quality scoring",
            "Priority": "High",
            "Why it matters": "Not all signals should carry the same editorial weight.",
            "Suggested implementation": "Score sources by authority, freshness, specificity, independence, and relevance to AfricaX pillars.",
        },
        {
            "Feature": "Entity extraction",
            "Priority": "High",
            "Why it matters": "The app should automatically identify founders, investors, companies, regulators, and institutions in each signal.",
            "Suggested implementation": "Use AI extraction into structured Person and Company records with confidence scores.",
        },
        {
            "Feature": "Opportunity workflow board",
            "Priority": "Medium",
            "Why it matters": "Good signals need follow-through: engage, interview, publish, sponsor, invite, or monitor.",
            "Suggested implementation": "Add kanban-style statuses for each recommended action.",
        },
        {
            "Feature": "Competitor and authority tracker",
            "Priority": "Medium",
            "Why it matters": "AfricaX needs to know where other publications dominate and where nobody owns the narrative.",
            "Suggested implementation": "Track coverage volume by topic/source and compare AfricaX publishing coverage.",
        },
        {
            "Feature": "Research dossier builder",
            "Priority": "Medium",
            "Why it matters": "High-value reports need source bundles, outlines, quotes, data points, and expert targets.",
            "Suggested implementation": "Turn selected signals into a report workspace with notes and source links.",
        },
        {
            "Feature": "Relationship reminders",
            "Priority": "Medium",
            "Why it matters": "The platform should move from passive intelligence to action.",
            "Suggested implementation": "Add next-action dates for people and companies, with weekly reminders.",
        },
    ]
    st.dataframe(pd.DataFrame(recommendations), use_container_width=True, height=420)
    st.subheader("Analyst recommendation")
    st.write(
        "The next most valuable product step is an evidence graph plus entity extraction. Once AOIP can reliably say "
        "which people, companies, countries, sources, and prior AfricaX notes support a recommendation, it becomes much "
        "more than a news monitor: it becomes a decision engine."
    )


def render_settings(settings: AppSettings) -> None:
    st.title("Settings")
    st.caption("Configure APIs, default markets, scan depth, backups, and demo mode.")
    with st.form("settings_form"):
        openai_api_key = st.text_input("OpenAI API Key", value=settings.openai_api_key, type="password")
        openai_model = st.text_input("OpenAI Model", value=settings.openai_model)
        embedding_model = st.text_input("Embedding Model", value=settings.embedding_model)
        google_api_key = st.text_input("Google API Key", value=settings.google_api_key, type="password")
        google_cse_id = st.text_input("Google Programmable Search Engine ID", value=settings.google_cse_id)
        countries = st.text_area("Default Countries", value=settings.default_countries)
        industries = st.text_area("Default Industries", value=settings.default_industries)
        scan_depth = st.slider("Items per source", 5, 100, settings.scan_depth)
        offline_demo_mode = st.toggle("Offline demo mode", value=settings.offline_demo_mode)
        submitted = st.form_submit_button("Save Settings")
    if submitted:
        save_settings(
            AppSettings(
                openai_api_key=openai_api_key,
                openai_model=openai_model,
                embedding_model=embedding_model,
                google_api_key=google_api_key,
                google_cse_id=google_cse_id,
                default_countries=countries,
                default_industries=industries,
                scan_depth=scan_depth,
                offline_demo_mode=offline_demo_mode,
            )
        )
        st.success("Settings saved.")
        st.rerun()
    if st.button("Create Database Backup"):
        path = backup_database()
        st.success(f"Backup created: {path}" if path else "No database exists yet.")


def show_conversation_table(conversations: list[Conversation], height: int = 380) -> None:
    if not conversations:
        st.info("No signals yet. Add sources or manual signals to begin.")
        return
    rows = [
        {
            "Title": c.title,
            "Source": c.source,
            "Open": c.url,
            "Country": c.country,
            "Industry": c.industry,
            "Pillar": c.pillar,
            "Opportunity": c.opportunity_score,
            "Relationship": c.relationship_score,
            "Authority": c.authority_score,
            "Action": c.recommended_action,
            "Summary": c.summary,
        }
        for c in conversations
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        height=height,
        column_config=link_column_config(),
    )


def link_column_config() -> dict[str, object]:
    return {"Open": st.column_config.LinkColumn("Open", display_text="Open")}


def matching_conversations_for_topic(conversations: list[Conversation], topic: str) -> list[Conversation]:
    needle = topic.lower()
    return [
        conversation
        for conversation in conversations
        if needle in f"{conversation.title} {conversation.summary} {conversation.content} {conversation.country} {conversation.industry}".lower()
    ]


def load_conversations() -> list[Conversation]:
    with session_scope() as session:
        return list(session.query(Conversation).order_by(Conversation.opportunity_score.desc()).all())


def load_people() -> list[Person]:
    with session_scope() as session:
        return list(session.query(Person).order_by(Person.relationship_score.desc()).all())


def load_companies() -> list[Company]:
    with session_scope() as session:
        return list(session.query(Company).order_by(Company.partnership_score.desc()).all())


def save_report(title: str, report_type: str, markdown: str, path: Path) -> None:
    with session_scope() as session:
        session.add(Report(title=title, report_type=report_type, body_markdown=markdown, export_path=str(path)))


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
