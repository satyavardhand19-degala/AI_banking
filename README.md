# ⬡ Vaani — Smart Data Intelligence

> **Vaani** *(Sanskrit: voice/speech)* — Enterprise-grade natural language interface for your private data vault, powered by **Programmatic Rule-based Analysis** and **Sarvam AI Voice**.

---

## Overview

**Vaani** lets business teams query their own data—CSVs, Excel sheets, or databases—using plain English **typed or spoken aloud**. The system:

1. **Uploads Data:** Users drag and drop CSV/Excel files into a secure **Supabase PostgreSQL** vault.
2. **Rule-based Analysis:** Translates natural language queries into validated PostgreSQL SQL using a high-performance programmatic rule engine (no LLM required for SQL generation).
3. **Smart Summary:** Generates a human-readable summary of findings using deterministic programmatic logic.
4. **Sarvam AI Voice:** Transcribes voice input (`saarika:v2`) and reads results aloud (`bulbul:v1`) in 11 Indian languages.

---

## Key Features

| # | Feature | Detail |
|---|---------|--------|
| 📊 | **Rule Engine** | Deterministic natural language to SQL translation |
| 🎙️ | **Voice Input** | Speak queries via Sarvam `saarika:v2` in 11 Indian languages |
| 📝 | **Smart Summary** | Programmatic analysis summaries read aloud via Sarvam `bulbul:v1` |
| 🔒 | **Secure Data Vault** | Data is stored in a managed Supabase PostgreSQL environment |
| 📈 | **Auto Charts** | Bar, line, or big-number card — auto-detected from result shape |
| 📂 | **File Upload** | Drag & drop CSV/Excel files; schema auto-detected and stored dynamically |

---

## Tech Stack

| Layer | Technology |
|-------|-----------:|
| Frontend | Plain HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Voice — STT | Sarvam AI `saarika:v2` (11 Indian languages) |
| Voice — TTS | Sarvam AI `bulbul:v1` (Natural Indian voices) |
| Database | Supabase (Managed PostgreSQL) |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/vaani-data-assistant.git
cd vaani-data-assistant

# 2. Configure
cp .env.example backend/.env
# MANDATORY: Fill in Supabase & Sarvam API credentials in backend/.env

# 3. Backend Setup
cd backend
python -m venv win_venv && win_venv\Scripts\activate
pip install -r requirements.txt

# 4. Start the server
python -m uvicorn main:app --reload

# 5. Use
# Open → http://localhost:8000
```
