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
