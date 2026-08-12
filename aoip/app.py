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
from aoip.automation_social import run_demand_scan, run_social_scan
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
    DemandSignal,
    EditorialCalendarItem,
    KnowledgeItem,
    OpportunityReport,
    Person,
    Report,
    SearchQuery,
    SourceConfig,
    SocialSignal,
)
from aoip.reports.generator import content_gap_report, daily_brief, export_conversations_csv, export_markdown
from aoip.search.operators import DEFAULT_SITES, generate_search_operators
from aoip.vector_store import VectorStore


st.set_page_config(page_title="AOIP", page_icon="AX", layout="wide", initial_sidebar_state="expanded")

PLOTLY_COLORS = ["#A855F7", "#FF2FA3", "#22D3EE", "#F59E0B", "#7C3AED", "#E879F9"]


def main() -> None:
    init_db()
    settings = load_settings()
    if settings.offline_demo_mode:
        seed_demo_data()
    inject_css()

    render_sidebar_brand()
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Daily Scan",
            "Social Intelligence",
            "Demand Intelligence",
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
    elif page == "Social Intelligence":
        render_social_intelligence(settings)
    elif page == "Demand Intelligence":
        render_demand_intelligence(settings)
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
        :root {
            --ax-bg: #030409;
            --ax-bg-soft: #070A12;
            --ax-panel: rgba(11, 15, 26, 0.78);
            --ax-panel-strong: rgba(14, 18, 32, 0.94);
            --ax-border: rgba(168, 85, 247, 0.26);
            --ax-border-cyan: rgba(34, 211, 238, 0.28);
            --ax-text: #F4F7FB;
            --ax-muted: #9AA6B8;
            --ax-purple: #A855F7;
            --ax-magenta: #FF2FA3;
            --ax-cyan: #22D3EE;
            --ax-amber: #F59E0B;
            --ax-green: #22C55E;
        }
        .stApp {
            background:
                linear-gradient(90deg, rgba(168, 85, 247, 0.05), transparent 28%),
                radial-gradient(circle at 84% 8%, rgba(168, 85, 247, 0.13), transparent 24rem),
                radial-gradient(circle at 72% 62%, rgba(34, 211, 238, 0.07), transparent 28rem),
                var(--ax-bg);
            color: var(--ax-text);
        }
        .block-container {
            padding-top: 1.4rem;
            max-width: 1240px;
        }
        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(12, 14, 26, 0.98), rgba(4, 5, 12, 0.98)),
                #05060C;
            border-right: 1px solid rgba(148, 163, 184, 0.18);
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            color: #DDE5F0;
        }
        .ax-brand {
            padding: 1.15rem 0.35rem 1rem 0.35rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
            margin-bottom: 0.9rem;
        }
        .ax-logo {
            font-size: 1.55rem;
            line-height: 1;
            letter-spacing: 0.08em;
            font-weight: 800;
            color: #FFFFFF;
        }
        .ax-logo span {
            color: var(--ax-magenta);
            text-shadow: 0 0 18px rgba(255, 47, 163, 0.55);
        }
        .ax-sublogo {
            margin-top: 0.38rem;
            color: #AAB6C8;
            font-size: 0.72rem;
            letter-spacing: 0.32em;
            text-transform: uppercase;
        }
        .ax-sidebar-section {
            color: #8D9AAF;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.28em;
            margin: 1.1rem 0 0.35rem;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(17, 22, 38, 0.88), rgba(8, 10, 19, 0.92));
            border: 1px solid rgba(168, 85, 247, 0.23);
            border-radius: 8px;
            padding: 16px 18px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 0 24px rgba(168, 85, 247, 0.08);
        }
        div[data-testid="stMetric"] label {
            color: #AEB8C9 !important;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.72rem;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #F8FAFC;
            font-weight: 750;
        }
        .aoip-card {
            background:
                linear-gradient(135deg, rgba(255, 47, 163, 0.08), rgba(34, 211, 238, 0.025) 40%, rgba(10, 12, 22, 0.9)),
                var(--ax-panel);
            border: 1px solid rgba(255, 47, 163, 0.30);
            border-radius: 8px;
            padding: 22px;
            margin: 8px 0 16px 0;
            box-shadow: 0 0 34px rgba(255, 47, 163, 0.10), inset 0 1px 0 rgba(255,255,255,0.05);
        }
        .muted { color: var(--ax-muted); }
        h1, h2, h3 {
            color: var(--ax-text);
            letter-spacing: 0;
        }
        h2, h3 {
            text-transform: none;
        }
        .ax-kicker {
            color: var(--ax-magenta);
            letter-spacing: 0.22em;
            text-transform: uppercase;
            font-size: 0.76rem;
            font-weight: 800;
        }
        .ax-hero {
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(168, 85, 247, 0.23);
            border-radius: 8px;
            padding: 30px 32px;
            margin-bottom: 1.25rem;
            background:
                linear-gradient(135deg, rgba(168, 85, 247, 0.10), transparent 38%),
                linear-gradient(90deg, rgba(7, 10, 18, 0.96), rgba(8, 10, 20, 0.78)),
                var(--ax-panel);
            box-shadow: 0 0 44px rgba(168, 85, 247, 0.09);
        }
        .ax-hero:after {
            content: "";
            position: absolute;
            right: 24px;
            top: 26px;
            width: 185px;
            height: 185px;
            border-radius: 50%;
            border: 1px solid rgba(34, 211, 238, 0.22);
            box-shadow:
                inset 0 0 0 18px rgba(168, 85, 247, 0.04),
                inset 0 0 0 42px rgba(255, 47, 163, 0.035),
                0 0 26px rgba(34, 211, 238, 0.10);
            opacity: 0.75;
        }
        .ax-title {
            position: relative;
            z-index: 1;
            font-size: clamp(2.2rem, 5vw, 4.5rem);
            line-height: 0.95;
            font-weight: 850;
            letter-spacing: 0.02em;
            margin: 0.65rem 0 0.35rem;
        }
        .ax-title span {
            color: var(--ax-magenta);
            text-shadow: 0 0 20px rgba(255, 47, 163, 0.35);
        }
        .ax-deck {
            position: relative;
            z-index: 1;
            color: #C7D0DF;
            max-width: 720px;
            font-size: 1rem;
            line-height: 1.65;
        }
        .ax-card-header {
            color: var(--ax-magenta);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }
        .ax-badge-row {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin: 1rem 0 1.15rem;
        }
        .ax-badge {
            border: 1px solid rgba(168, 85, 247, 0.34);
            color: #E9D5FF;
            background: rgba(168, 85, 247, 0.10);
            border-radius: 8px;
            padding: 0.32rem 0.62rem;
            font-size: 0.78rem;
        }
        .ax-brief {
            border: 1px solid rgba(245, 158, 11, 0.22);
            background: rgba(245, 158, 11, 0.055);
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }
        .ax-status-amber { color: var(--ax-amber); }
        .ax-status-cyan { color: var(--ax-cyan); }
        .ax-status-magenta { color: var(--ax-magenta); }
        .stButton > button,
        .stLinkButton > a {
            background: rgba(15, 18, 32, 0.86);
            border: 1px solid rgba(255, 47, 163, 0.45);
            border-radius: 8px;
            color: #F8FAFC;
            box-shadow: 0 0 18px rgba(255, 47, 163, 0.10);
        }
        .stButton > button:hover,
        .stLinkButton > a:hover {
            border-color: rgba(34, 211, 238, 0.70);
            color: #FFFFFF;
            box-shadow: 0 0 22px rgba(34, 211, 238, 0.13);
        }
        div[data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 8px;
            overflow: hidden;
            background: rgba(7, 10, 18, 0.75);
        }
        div[data-testid="stExpander"] {
            border: 1px solid rgba(168, 85, 247, 0.18);
            border-radius: 8px;
            background: rgba(7, 10, 18, 0.62);
        }
        input, textarea, div[data-baseweb="select"] > div {
            background-color: rgba(7, 10, 18, 0.9) !important;
            border-color: rgba(148, 163, 184, 0.22) !important;
            color: var(--ax-text) !important;
        }
        hr {
            border-color: rgba(148, 163, 184, 0.15);
        }
        @media (max-width: 900px) {
            .ax-hero {
                padding: 24px 20px;
            }
            .ax-hero:after {
                opacity: 0.25;
                right: -60px;
            }
            .ax-title {
                font-size: 2.45rem;
            }
            .aoip-card [style*="grid-template-columns"] {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.sidebar.markdown(
        """
        <div class="ax-brand">
            <div class="ax-logo">AFRICA<span>X</span></div>
            <div class="ax-sublogo">Intelligence OS</div>
        </div>
        <div class="ax-sidebar-section">Command Centre</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, caption: str, tone: str) -> str:
    tone_class = {
        "purple": "ax-status-magenta",
        "magenta": "ax-status-magenta",
        "cyan": "ax-status-cyan",
        "amber": "ax-status-amber",
    }.get(tone, "ax-status-cyan")
    return f"""
    <div class="aoip-card">
        <div class="ax-card-header">{label}</div>
        <div style="font-size:2.55rem;font-weight:820;line-height:1;color:#F8FAFC;">{value}</div>
        <div class="{tone_class}" style="margin-top:0.7rem;font-size:0.88rem;">{caption}</div>
    </div>
    """


def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,4,9,0.25)",
        font={"color": "#DDE5F0"},
        margin={"l": 12, "r": 12, "t": 20, "b": 28},
        coloraxis_showscale=False,
        xaxis={
            "gridcolor": "rgba(148,163,184,0.12)",
            "zerolinecolor": "rgba(148,163,184,0.16)",
        },
        yaxis={
            "gridcolor": "rgba(148,163,184,0.08)",
            "zerolinecolor": "rgba(148,163,184,0.12)",
        },
    )
    return fig


def render_dashboard() -> None:
    conversations = load_conversations()
    people = load_people()
    companies = load_companies()
    social_signals = load_social_signals()
    demand_signals = load_demand_signals()

    st.markdown(
        """
        <div class="ax-hero">
            <div class="ax-kicker">Opportunity Intelligence Cockpit</div>
            <div class="ax-title">AFRICAX <span>SIGNAL</span></div>
            <div class="ax-deck">
                The highest-leverage intelligence cockpit for AfricaX editorial, research,
                relationship, demand, and authority decisions.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].markdown(metric_card("Signals Today", str(len(conversations)), "Conversation evidence", "magenta"), unsafe_allow_html=True)
    metric_cols[1].markdown(metric_card("Avg Opportunity", f"{avg([c.opportunity_score for c in conversations]):.0f}", "High potential", "purple"), unsafe_allow_html=True)
    metric_cols[2].markdown(metric_card("Social Signals", str(len(social_signals)), "Reddit and YouTube", "cyan"), unsafe_allow_html=True)
    metric_cols[3].markdown(metric_card("Demand Signals", str(len(demand_signals)), "Search demand", "amber"), unsafe_allow_html=True)

    top = sorted(conversations, key=lambda item: item.opportunity_score, reverse=True)[:1]
    if top:
        best = top[0]
        st.markdown(
            f"""
            <div class="aoip-card">
                <div class="ax-card-header">Highest-Leverage Move</div>
                <h3>{best.title}</h3>
                <div class="ax-badge-row">
                    <span class="ax-badge">{best.country or "Africa"}</span>
                    <span class="ax-badge">{best.industry or "General"}</span>
                    <span class="ax-badge">{best.pillar or "Intelligence"}</span>
                </div>
                <p class="muted">{best.summary}</p>
                <div class="ax-brief">
                    <strong>Recommended action:</strong> <span class="ax-status-magenta">{best.recommended_action}</span><br/>
                    <strong>Follow-up question:</strong> {best.follow_up_question}
                </div>
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
            fig = px.bar(
                df,
                x="score",
                y="industry",
                orientation="h",
                color="score",
                color_continuous_scale=["#F59E0B", "#FF2FA3", "#A855F7"],
            )
            st.plotly_chart(style_plotly(fig), use_container_width=True)

    high_priority = len([c for c in conversations if c.opportunity_score >= 75])
    emerging_themes = len({c.industry for c in conversations if c.industry and c.opportunity_score >= 60})
    follow_ups = len([c for c in conversations if c.relationship_score >= 60])
    st.markdown(
        f"""
        <div class="aoip-card">
            <div class="ax-card-header">Today's Intelligence Brief</div>
            <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:1rem;">
                <div><div style="font-size:1.55rem;font-weight:800;">{high_priority}</div><div class="muted">High-priority opportunities</div></div>
                <div><div style="font-size:1.55rem;font-weight:800;color:var(--ax-amber);">{emerging_themes}</div><div class="muted">Emerging themes</div></div>
                <div><div style="font-size:1.55rem;font-weight:800;color:var(--ax-cyan);">{follow_ups}</div><div class="muted">Relationship follow-ups</div></div>
                <div><div style="font-size:1.05rem;font-weight:800;color:var(--ax-amber);">Operational</div><div class="muted">Source health ready</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
            kind = st.selectbox(
                "Source type",
                [
                    "rss",
                    "google_news_rss",
                    "social_reddit_rss",
                    "social_youtube_discovery",
                    "social_youtube_channel_rss",
                    "demand_google_news_rss",
                    "official_api",
                    "manual",
                ],
            )
            url = st.text_input("Feed or API URL")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save Source")
        if submitted and name:
            with session_scope() as session:
                session.add(SourceConfig(name=name, kind=kind, url=url, notes=notes))
            st.success("Source saved.")
            st.rerun()


def render_social_intelligence(settings: AppSettings) -> None:
    st.title("Social Intelligence")
    st.caption("No LinkedIn or Meta account required. This uses public Reddit RSS/search feeds and YouTube discovery feeds.")
    c1, c2, c3 = st.columns(3)
    social_signals = load_social_signals()
    c1.metric("Social Signals", len(social_signals))
    c2.metric("Avg Opportunity", f"{avg([s.opportunity_score for s in social_signals]):.0f}")
    c3.metric("Platforms", len({s.platform for s in social_signals}))

    if st.button("Run Social Scan", type="primary"):
        with st.spinner("Scanning Reddit and YouTube discovery feeds..."):
            count = run_social_scan(settings)
        st.success(f"Social scan complete. Added {count} new social signals.")
        st.rerun()

    st.subheader("Social Sources")
    with session_scope() as session:
        sources = (
            session.query(SourceConfig)
            .filter(SourceConfig.kind.in_(["social_reddit_rss", "social_youtube_discovery", "social_youtube_channel_rss"]))
            .order_by(SourceConfig.name)
            .all()
        )
    st.dataframe(
        pd.DataFrame(
            [
                {"Name": s.name, "Kind": s.kind, "Open": s.url, "Active": s.is_active, "Notes": s.notes}
                for s in sources
            ]
        ),
        use_container_width=True,
        column_config=link_column_config(),
    )

    if st.button("Check Social Source Health"):
        rows = []
        with st.spinner("Checking social feeds..."):
            for source in sources:
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

    with st.expander("Add Reddit or YouTube feed"):
        st.write("Use Reddit search RSS, Google News RSS for YouTube discovery, or a YouTube channel RSS feed.")
        with st.form("add_social_source"):
            name = st.text_input("Name", placeholder="Reddit - Africa AI operators")
            kind = st.selectbox("Type", ["social_reddit_rss", "social_youtube_discovery", "social_youtube_channel_rss"])
            url = st.text_input("Feed URL", placeholder="https://www.reddit.com/search.rss?q=Africa%20AI%20startup&sort=new")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Save Social Source")
        if submitted and name and url:
            with session_scope() as session:
                session.add(SourceConfig(name=name, kind=kind, url=url, notes=notes))
            st.success("Social source saved.")
            st.rerun()

    st.subheader("Latest Social Signals")
    show_social_signal_table(social_signals)


def render_demand_intelligence(settings: AppSettings) -> None:
    st.title("Demand Intelligence")
    st.caption("Google demand/search evidence for what Africa-focused operators, founders, investors, and readers are trying to understand.")
    signals = load_demand_signals()
    c1, c2, c3 = st.columns(3)
    c1.metric("Demand Signals", len(signals))
    c2.metric("Avg Demand", f"{avg([s.demand_score for s in signals]):.0f}")
    c3.metric("Avg Authority Gap", f"{avg([s.authority_gap_score for s in signals]):.0f}")

    if st.button("Run Demand Scan", type="primary"):
        with st.spinner("Checking Google News demand monitors and generating Google Trends evidence links..."):
            count = run_demand_scan(settings)
        st.success(f"Demand scan complete. Added {count} demand signals.")
        st.rerun()

    st.subheader("Demand Opportunities")
    show_demand_signal_table(signals)

    st.subheader("Top Content Recommendations")
    for signal in sorted(signals, key=lambda item: item.demand_score + item.authority_gap_score, reverse=True)[:5]:
        st.markdown(f"**{signal.suggested_title}**")
        st.caption(f"{signal.topic} | {signal.industry or 'general'} | demand {signal.demand_score:.0f} | gap {signal.authority_gap_score:.0f}")
        st.write(signal.suggested_outline)
        if signal.evidence_url:
            st.link_button("Open Google Trends evidence", signal.evidence_url, key=f"demand-trends-{signal.id}")


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
    fig = px.scatter(
        df,
        x="signals",
        y="strength",
        size="strength",
        color="direction",
        hover_name="topic",
        color_discrete_sequence=PLOTLY_COLORS,
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)
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
        {
            "Feature": "Social conversation clustering",
            "Priority": "High",
            "Why it matters": "Reddit and YouTube signals should reveal repeated questions, objections, and underserved audience needs.",
            "Suggested implementation": "Cluster social signals by question pattern, industry, country, and suggested AfricaX response.",
        },
        {
            "Feature": "Google demand tracker",
            "Priority": "High",
            "Why it matters": "Search demand shows what people are actively trying to understand, even when they are not discussing it on social platforms.",
            "Suggested implementation": "Use Google News RSS evidence, Google Trends links, and later Google Trends BigQuery/API Alpha when access is available.",
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


def show_social_signal_table(signals: list[SocialSignal], height: int = 420) -> None:
    if not signals:
        st.info("No social signals yet. Run Social Scan to collect Reddit and YouTube discovery signals.")
        return
    rows = [
        {
            "Title": signal.title,
            "Platform": signal.platform,
            "Source": signal.source,
            "Open": signal.url,
            "Country": signal.country,
            "Industry": signal.industry,
            "Type": signal.signal_type,
            "Opportunity": signal.opportunity_score,
            "Relationship": signal.relationship_score,
            "Authority": signal.authority_score,
            "Suggested Reply": signal.suggested_reply,
            "Follow-up Question": signal.follow_up_question,
            "Status": signal.status,
        }
        for signal in signals
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        height=height,
        column_config=link_column_config(),
    )


def show_demand_signal_table(signals: list[DemandSignal], height: int = 420) -> None:
    if not signals:
        st.info("No demand signals yet. Run Demand Scan to generate demand intelligence.")
        return
    rows = [
        {
            "Topic": signal.topic,
            "Query": signal.query,
            "Country": signal.country,
            "Industry": signal.industry,
            "Source": signal.source,
            "Open": signal.evidence_url,
            "Evidence Count": signal.evidence_count,
            "Demand": signal.demand_score,
            "Authority Gap": signal.authority_gap_score,
            "Recommended Content": signal.recommended_content,
            "Suggested Title": signal.suggested_title,
            "Status": signal.status,
        }
        for signal in signals
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        height=height,
        column_config=link_column_config(),
    )


def load_conversations() -> list[Conversation]:
    with session_scope() as session:
        return list(session.query(Conversation).order_by(Conversation.opportunity_score.desc()).all())


def load_people() -> list[Person]:
    with session_scope() as session:
        return list(session.query(Person).order_by(Person.relationship_score.desc()).all())


def load_companies() -> list[Company]:
    with session_scope() as session:
        return list(session.query(Company).order_by(Company.partnership_score.desc()).all())


def load_social_signals() -> list[SocialSignal]:
    with session_scope() as session:
        return list(session.query(SocialSignal).order_by(SocialSignal.created_at.desc()).all())


def load_demand_signals() -> list[DemandSignal]:
    with session_scope() as session:
        return list(session.query(DemandSignal).order_by(DemandSignal.demand_score.desc()).all())


def save_report(title: str, report_type: str, markdown: str, path: Path) -> None:
    with session_scope() as session:
        session.add(Report(title=title, report_type=report_type, body_markdown=markdown, export_path=str(path)))


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
