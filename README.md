# AFRICAX Opportunity Intelligence Platform (AOIP)

AOIP is a private AI intelligence engine for AfricaX. It combines editorial intelligence, relationship intelligence, trend monitoring, content gap detection, opportunity scoring, and a searchable second brain in a Streamlit desktop app.

This build is intentionally modular:

- **Streamlit UI** for non-developer use.
- **SQLite + SQLAlchemy ORM** for local persistence with automatic schema creation and backups.
- **ChromaDB** for semantic memory.
- **OpenAI GPT-5.5 + embeddings** when an API key is configured.
- **RSS, Google Programmable Search, and Google News RSS** connectors.
- **Offline demo intelligence** so the app remains usable before API keys are added.

## Quick Start

1. Double-click `install.bat`.
2. Double-click `launch.bat`.
3. Open the local Streamlit URL shown by the launcher.
4. Add API keys in **Settings**.

## Safe Data Collection

AOIP is not a scraper. Connectors are designed for Google Programmable Search API, Google News RSS, RSS feeds, official APIs, and user-imported notes/reports/articles.

## Source Library

The app seeds a broader source library on startup, including official feeds and reputable Africa business/technology sources:

- African Development Bank
- Central Bank of Nigeria circulars and publications
- World Bank Africa
- TechCabal
- Techpoint Africa
- Disrupt Africa
- IT News Africa
- African Business
- Business Post Nigeria
- Ventures Africa
- How We Made It In Africa
- Google News RSS monitors for startup funding, AI infrastructure, fintech regulation, climate finance, trade, energy infrastructure, digital economy policy, and market expansion

Use **Daily Scan -> Check Source Health** to confirm that active sources are returning items and original links.

## Evidence Links

Conversation tables now include an **Open** link column. Use it to inspect the original article, feed item, or Google News result behind each signal. Trend and content-gap pages also expose their supporting evidence signals.

## Social Intelligence Without Special API Access

AOIP includes a **Social Intelligence** page that avoids LinkedIn/Meta account integrations and avoids private API keys. It uses:

- Reddit public search RSS feeds for startup, founder, fintech, AI, climate finance, and Africa business discussions.
- Google News RSS discovery queries scoped to YouTube for Africa business, startup, AI, and podcast/video signals.
- Optional YouTube channel RSS feeds that can be added from the UI.

Run **Social Intelligence -> Run Social Scan** to save social signals and convert them into the main Conversation Intelligence workflow.

## Demand Intelligence

AOIP includes a **Demand Intelligence** page for Google-based demand signals. It uses Google News RSS evidence and Google Trends explore links to track topics such as startup funding, AI business opportunities, fintech regulation, climate finance, AfCFTA, manufacturing, healthtech, edtech, creator economy, and infrastructure investment.

Run **Demand Intelligence -> Run Demand Scan** to generate:

- Demand score
- Authority gap score
- Evidence count
- Google Trends evidence link
- Suggested AfricaX title
- Suggested outline
- Recommended content format

## Tests

```powershell
python -m pytest
```

## Project Structure

```text
aoip/
  app.py
  ai.py
  config.py
  db.py
  models.py
  vector_store.py
  automation.py
  connectors/
  intelligence/
  reports/
  search/
tests/
```
