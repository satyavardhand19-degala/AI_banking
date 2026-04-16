# Deployment Guide — Vaani Smart Data Intelligence

**Version:** 2.5 (Programmatic + Sarvam Edition)  
**Last Updated:** April 2026

## Overview
Vaani v2.5 is optimized for deployment as a deterministic data assistant using a rule-based engine and Sarvam AI for voice.

---

## 🚀 Production Infrastructure

### 1. Supabase Backend
Ensure your database is initialized:
1. Run `supabase/schema.sql` in the Supabase SQL Editor.
2. Setup your **Database Host**, **User**, and **Password**.

### 2. Required Environment Variables
| Variable | Usage |
|----------|-------|
| `SUPABASE_URL` | Project API URL |
| `SUPABASE_SERVICE_KEY` | Admin API access |
| `SUPABASE_DB_HOST` | PostgreSQL Host address |
| `SUPABASE_DB_PASSWORD` | PostgreSQL Database password |
| `SARVAM_API_KEY` | **Mandatory** for Voice features (STT/TTS) |
| `APP_ENV` | Set to `production` |

---

## 🛠️ Deployment Options

### Option A: Docker (Recommended)
Use the provided `Dockerfile`.

```bash
docker build -t vaani-intelligence .
docker run -p 8000:8000 \
  -e SUPABASE_DB_HOST=your_host \
  -e SARVAM_API_KEY=your_key \
  vaani-intelligence
```

### Option B: Render.com
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn main:app --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker`

---

## 🔒 Security & Optimization Tips
- **Deterministic Logic:** Since the system uses a Rule Engine, SQL injection is strictly prevented by the `sql_validator.py`.
- **HTTPS:** **Mandatory** for the microphone to work in the browser.
