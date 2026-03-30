# 🏦 Vaani — AI Banking Intelligence

> **वाणी** *(Sanskrit: voice/speech)* — Enterprise-grade natural language + voice interface for structured banking data, powered by Claude AI, Sarvam AI Voice, FastAPI, and Supabase.

---

## Overview

**Vaani** lets banking business teams query live data — customers, accounts, transactions — using plain English **typed or spoken aloud in Indian languages**. The system:

1. Accepts text input **or** microphone voice via Sarvam AI Speech-to-Text (`saarika:v2`)
2. Translates the query to a validated PostgreSQL `SELECT` via Claude AI
3. Executes it against a Supabase PostgreSQL database (read-only)
4. Renders the result in a **premium dark dashboard** — sortable tables + auto-detected charts
5. Reads the result summary aloud via Sarvam AI Text-to-Speech (`bulbul:v1`)

No SQL knowledge required. No engineering dependency. Works in 11 Indian languages.

---

## Key Features

| # | Feature | Detail |
|---|---------|--------|
| 🎙️ | **Voice Input — Sarvam STT** | Speak queries; `saarika:v2` transcribes in real time |
| 🔊 | **Voice Output — Sarvam TTS** | Result summaries read aloud via `bulbul:v1` |
| 🌐 | **11 Indian Languages** | Hindi, Tamil, Telugu, Kannada, Bengali, Marathi, Gujarati, Malayalam, Odia, Punjabi + English |
| 🤖 | **Claude AI → SQL** | Natural language converted to validated read-only SQL |
| 🔒 | **Read-Only Enforcement** | `INSERT/UPDATE/DELETE/DROP` blocked unconditionally |
| 📊 | **Auto Charts** | Bar, line, or big-number card — auto-detected from result shape |
| 🎨 | **Premium Dark UI** | Luxury navy/gold design system — fully custom, no templates |
| ⚡ | **Supabase Backend** | Managed PostgreSQL + psycopg2 connection pooling |
| 🛡️ | **SQL Injection Prevention** | Allowlist validation — no raw user input in SQL |
| 🏗️ | **Modular Architecture** | Clean layered backend: AI / Voice / DB / Validator |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Plain HTML5, CSS3, Vanilla JavaScript (zero frameworks) |
| UI Design | Custom dark luxury theme — Instrument Serif + Syne + JetBrains Mono |
| Charts | Chart.js 4.x — teal/gold palette, auto-detected chart types |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| AI — Text | Anthropic Claude API (`claude-sonnet-4-20250514`) |
| Voice — STT | Sarvam AI `saarika:v2` (Speech-to-Text, 11 Indian languages) |
| Voice — TTS | Sarvam AI `bulbul:v1` (Text-to-Speech, natural Indian voices) |
| Database | Supabase — PostgreSQL 15, psycopg2 threaded connection pool |
| Row Security | Supabase RLS — SELECT-only service role |
| Deployment | Supabase (DB) + Render / Railway / self-hosted VPS |

---

## Voice Architecture — Sarvam AI

```
User speaks into mic
        │
        ▼
Browser MediaRecorder API  (captures WebM/opus audio blob)
        │
        ▼
POST /api/voice/transcribe
  └─► FastAPI backend ──► Sarvam STT (saarika:v2)
                          api.sarvam.ai/speech-to-text
        │
        ▼
Transcribed text string
        │
        ▼
Claude AI SQL pipeline  (identical to typed query flow)
        │
        ▼
Results rendered (sortable table + Chart.js)
        │
        ▼
Summary string built from result rows
        │
        ▼
POST /api/voice/speak
  └─► FastAPI backend ──► Sarvam TTS (bulbul:v1)
                          api.sarvam.ai/text-to-speech
        │
        ▼
Audio bytes streamed back → Web Audio API plays aloud 🔊
```

### Sarvam API Reference

| Purpose | Endpoint | Model |
|---------|----------|-------|
| Speech-to-Text | `POST https://api.sarvam.ai/speech-to-text` | `saarika:v2` |
| Text-to-Speech | `POST https://api.sarvam.ai/text-to-speech` | `bulbul:v1` |

**Supported language codes:**
`en-IN` · `hi-IN` · `ta-IN` · `te-IN` · `kn-IN` · `bn-IN` · `mr-IN` · `gu-IN` · `ml-IN` · `or-IN` · `pa-IN`

---

## UI Design System

The frontend is a **fully custom premium dark banking dashboard** — no Streamlit, no templates, no scaffolding tools.

| Element | Specification |
|---------|--------------|
| Background | Deep navy void `#050810` + gold grid overlay CSS pattern |
| Primary accent | Liquid gold `#d4a853` |
| Secondary accent | Teal `#2dd4bf` |
| Display font | **Instrument Serif** — italic editorial headers |
| UI / label font | **Syne** — geometric, high-clarity |
| Code / SQL font | **JetBrains Mono** |
| Card style | Glassmorphism — `backdrop-filter: blur` + subtle gold border |
| Mic button | Animated pulse-ring + live waveform bars while recording |
| Language picker | Dropdown (11 Sarvam languages) embedded in query panel |
| Chart colors | Teal bars · gold line · navy area fill |
| Animations | CSS staggered reveal on load; result rows slide in sequentially |
| SQL display | Collapsible monospace code box with syntax-highlight classes |
| Responsive | Sidebar collapses on mobile → full-width single column |

### Layout Zones

```
┌───────────────────────────────────────────────────────────────┐
│  HEADER: Logo · "Vaani" · DB status pill · Language selector   │
├──────────────────┬────────────────────────────────────────────┤
│                  │  QUERY INPUT PANEL                          │
│  HISTORY         │  ┌──────────────────────────────────────┐  │
│  SIDEBAR         │  │ Textarea (placeholder: try typing or  │  │
│                  │  │ speaking a query...)                  │  │
│  Last 10 queries │  │                                       │  │
│  clickable to    │  │ [🎙 Mic]  [Language ▾]  [Ask →]       │  │
│  re-run          │  │  Ctrl+Enter shortcut hint             │  │
│                  │  └──────────────────────────────────────┘  │
│                  ├────────────────────────────────────────────┤
│                  │  RESULTS PANEL                             │
│                  │  SQL badge (collapsible) · Row count ·     │
│                  │  🔊 Speak result button                    │
│                  │  ─────────────────────────────────────     │
│                  │  Chart.js visualization (auto-detected)    │
│                  │  Sortable data table                       │
└──────────────────┴────────────────────────────────────────────┘
```

---

## Project Structure

```
vaani-banking-assistant/
├── backend/
│   ├── main.py                    # FastAPI app, CORS, startup event
│   ├── config.py                  # Pydantic BaseSettings — all env vars
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          # psycopg2 ThreadedConnectionPool
│   │   └── executor.py            # Read-only SQL executor (30s timeout)
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── claude_client.py       # Anthropic API wrapper
│   │   └── prompt_builder.py      # Schema-aware prompt + JOIN examples
│   ├── voice/
│   │   ├── __init__.py
│   │   ├── sarvam_stt.py          # Sarvam STT client (saarika:v2)
│   │   ├── sarvam_tts.py          # Sarvam TTS client (bulbul:v1)
│   │   └── summary_builder.py     # Result rows → speakable summary
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # All FastAPI routes
│   │   └── models.py              # Pydantic request/response models
│   ├── validators/
│   │   ├── __init__.py
│   │   └── sql_validator.py       # 6-step SQL safety enforcement
│   └── requirements.txt
├── frontend/
│   ├── index.html                 # Premium dark single-page UI
│   ├── css/
│   │   └── styles.css             # Full custom design system
│   └── js/
│       ├── app.js                 # Orchestration, history, render, toast
│       ├── api.js                 # Backend HTTP client
│       ├── voice.js               # MediaRecorder + Sarvam flow + waveform
│       └── charts.js              # Chart.js auto-detect + render
├── supabase/
│   ├── schema.sql
│   ├── seed.sql
│   └── rls_policies.sql
├── docs/
│   ├── README.md
│   ├── scope.md
│   ├── specification.md
│   ├── deploy.md
│   └── prompt.md
├── .env.example
└── .gitignore
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/vaani-banking-assistant.git
cd vaani-banking-assistant

# 2. Configure
cp .env.example .env
# Fill in: Supabase, Anthropic, and Sarvam credentials

# 3. Initialize Supabase DB (SQL Editor — run in this order)
#    supabase/schema.sql  →  seed.sql  →  rls_policies.sql

# 4. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 5. Frontend
python -m http.server 3000 --directory ../frontend
# Open → http://localhost:3000
```

---

## Example Queries — Typed or Spoken

```
Show the last 10 transactions where amount is greater than 10,000
How many transactions today have amount greater than 10,000?
List customers who performed transactions above 50,000 this week
Show total credit transactions for today
Display account balance details for customer ID 101
Show recent debit transactions for account number 5001
```

Click **mic** → speak in your language → Sarvam transcribes → results appear → summary plays aloud.

---

## Security

| Control | Implementation |
|---------|---------------|
| Read-only SQL | 6-step validator — all non-SELECT unconditionally blocked |
| DB privileges | Supabase service role: SELECT-only grants |
| No SQL injection | Claude generates SQL; no user text interpolated into queries |
| Sarvam key protected | Server-side only — never sent to the browser |
| Audio privacy | Blobs processed in memory and discarded after transcription |
| CORS | Restricted to configured origins in production |
| Error sanitization | Stack traces never exposed in API response bodies |
| Query timeout | 30-second hard limit per database statement |

---

## License

MIT — see `LICENSE` for details.
