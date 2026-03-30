# Deployment Guide — Vaani AI Banking Data Assistant

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.11+ | Backend runtime |
| pip 23+ | Package manager |
| Supabase account | [supabase.com](https://supabase.com) — free tier works |
| Anthropic API key | [console.anthropic.com](https://console.anthropic.com) |
| Sarvam AI API key | [dashboard.sarvam.ai](https://dashboard.sarvam.ai) — register for access |
| HTTPS in production | **Required** — browsers block `getUserMedia` (mic) on plain HTTP |

> ⚠️ **Voice requires HTTPS.** The browser's `getUserMedia` API used for mic capture is only available on `localhost` or over a valid HTTPS connection. HTTP production deployments will have the mic button automatically disabled.

---

## Step 1: Supabase Setup

### 1.1 Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) → **New Project**
2. Set project name: `vaani-banking-assistant`
3. Set a strong database password — **save it**
4. Choose the region closest to your users
5. Click **Create new project** — wait ~2 minutes

### 1.2 Collect Supabase Credentials

**From Settings → API:**
```
SUPABASE_URL          → Project URL  (e.g. https://abcxyz.supabase.co)
SUPABASE_SERVICE_KEY  → service_role key  (under "Project API keys")
```

**From Settings → Database:**
```
SUPABASE_DB_HOST      → Host  (e.g. db.abcxyz.supabase.co)
SUPABASE_DB_PORT      → 5432
SUPABASE_DB_NAME      → postgres
SUPABASE_DB_USER      → postgres
SUPABASE_DB_PASSWORD  → (password set in step 1.1)
```

### 1.3 Initialize the Database

In **Supabase Dashboard → SQL Editor**, run the files in this exact order:

**A — Schema (tables + indexes):**
```
Paste contents of:  supabase/schema.sql  → Run
```

**B — Seed data:**
```
Paste contents of:  supabase/seed.sql  → Run
```

**C — Row Level Security:**
```
Paste contents of:  supabase/rls_policies.sql  → Run
```

Verify in **Table Editor** that `customers`, `accounts`, `transactions` are created with sample data.

---

## Step 2: Sarvam AI Setup

### 2.1 Obtain API Key

1. Register at [dashboard.sarvam.ai](https://dashboard.sarvam.ai)
2. Create a project → copy the **API Subscription Key**
3. This is your `SARVAM_API_KEY`

### 2.2 Verify Access

Test STT access (replace `YOUR_KEY`):
```bash
curl -X POST https://api.sarvam.ai/speech-to-text \
  -H "api-subscription-key: YOUR_KEY" \
  -F "model=saarika:v2" \
  -F "language_code=en-IN" \
  -F "file=@test.wav"
```
Expected: `{"transcript": "..."}` — confirms STT is active.

Test TTS access:
```bash
curl -X POST https://api.sarvam.ai/text-to-speech \
  -H "api-subscription-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inputs":["Hello, this is a test."],"target_language_code":"en-IN","model":"bulbul:v1"}' \
  --output test_output.wav
```
Expected: `test_output.wav` is a valid audio file.

### 2.3 Supported Languages

| Language | Code |
|----------|------|
| English (India) | `en-IN` |
| Hindi | `hi-IN` |
| Tamil | `ta-IN` |
| Telugu | `te-IN` |
| Kannada | `kn-IN` |
| Bengali | `bn-IN` |
| Marathi | `mr-IN` |
| Gujarati | `gu-IN` |
| Malayalam | `ml-IN` |
| Odia | `or-IN` |
| Punjabi | `pa-IN` |

---

## Step 3: Clone & Configure

```bash
git clone https://github.com/your-org/vaani-banking-assistant.git
cd vaani-banking-assistant

cp .env.example .env
```

Edit `.env` with all credentials:

```env
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...YOUR_SERVICE_ROLE_KEY
SUPABASE_DB_HOST=db.YOUR_PROJECT_REF.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=YOUR_DB_PASSWORD

ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY

SARVAM_API_KEY=YOUR_SARVAM_SUBSCRIPTION_KEY

ALLOWED_ORIGINS=http://localhost:3000
APP_ENV=development
```

---

## Step 4: Backend Setup

```bash
cd backend

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Verify config loads
python -c "from config import settings; print('OK:', settings.app_env)"

# Start dev server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify all endpoints

```bash
# Health check
curl http://localhost:8000/api/health
# → {"status":"ok","db":"connected"}

# Text query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Show the last 5 transactions"}'
# → {"success":true,"sql":"SELECT ...","columns":[...],"rows":[...],"count":5,...}

# TTS (save audio)
curl -X POST http://localhost:8000/api/voice/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Found 5 results.","language_code":"en-IN"}' \
  --output response.wav
# → response.wav should be a valid audio file
```

---

## Step 5: Frontend Setup

Update `frontend/js/api.js` — set the backend URL:

```javascript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production — update to your deployed backend URL
// const API_BASE_URL = 'https://your-api.render.com';
```

Serve locally:
```bash
python -m http.server 3000 --directory frontend
# Open → http://localhost:3000
```

> **Note:** Mic button works on `localhost` without HTTPS. For production, HTTPS is mandatory.

---

## Step 6: End-to-End Verification

Test these queries in the UI (text and voice):

```
1. Show the last 10 transactions where amount is greater than 10000
   → Should show a table of 10 rows

2. How many transactions today have amount greater than 10000?
   → Should show a big-number card + count

3. Display account balance details for customer ID 1
   → Should show account rows for that customer

4. Show total credit transactions for today
   → Should show aggregated sum

5. List customers who performed transactions above 50000 this week
   → Should show customer names via JOIN
```

For voice: select a language → click mic → speak query 1 above → verify transcript appears → verify audio playback of summary.

---

## Production Deployment

### Option A: Render.com (Recommended)

**Backend (Web Service):**
1. Push code to GitHub
2. Render Dashboard → New → **Web Service** → connect repo
3. Configure:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add all `.env` variables under **Environment**
5. Enable **Auto-Deploy**

**Frontend (Static Site):**
1. Render Dashboard → New → **Static Site** → connect same repo
2. Root Directory: `frontend`
3. No build command needed
4. Update `js/api.js` → `API_BASE_URL` to your Render backend URL
5. Update backend `ALLOWED_ORIGINS` to include Render frontend URL

Render provides automatic HTTPS → mic button works.

### Option B: Railway.app

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

Set environment variables:
```bash
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set SARVAM_API_KEY=your-key
railway variables set SUPABASE_URL=https://...
railway variables set SUPABASE_SERVICE_KEY=eyJ...
railway variables set SUPABASE_DB_HOST=db....
railway variables set SUPABASE_DB_PASSWORD=...
railway variables set ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

Railway provides automatic HTTPS on all deployments.

### Option C: Self-Hosted VPS (with HTTPS via Let's Encrypt)

```bash
# Install system deps
sudo apt update && sudo apt install -y python3.11 python3-pip nginx certbot python3-certbot-nginx

# App setup
git clone ... && cd vaani-banking-assistant
cp .env.example .env && nano .env

# Backend
cd backend && pip install -r requirements.txt gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 --daemon --log-file /var/log/vaani.log

# Copy frontend
sudo mkdir -p /var/www/vaani
sudo cp -r frontend/* /var/www/vaani/
```

**Nginx config** (`/etc/nginx/sites-available/vaani`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;    # for audio file uploads
    }

    location / {
        root /var/www/vaani;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vaani /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Enable HTTPS (required for mic!)
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Supabase project API URL |
| `SUPABASE_SERVICE_KEY` | ✅ | service_role API key |
| `SUPABASE_DB_HOST` | ✅ | PostgreSQL host |
| `SUPABASE_DB_PORT` | ✅ | 5432 |
| `SUPABASE_DB_NAME` | ✅ | postgres |
| `SUPABASE_DB_USER` | ✅ | postgres |
| `SUPABASE_DB_PASSWORD` | ✅ | Database password |
| `ANTHROPIC_API_KEY` | ✅ | Claude API key |
| `SARVAM_API_KEY` | ✅ | Sarvam AI subscription key |
| `ALLOWED_ORIGINS` | ✅ | CORS origins (comma-separated) |
| `APP_ENV` | ⬜ | `development` or `production` |

---

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| `Missing SARVAM_API_KEY` | Add to `.env`; get key from `dashboard.sarvam.ai` |
| Mic button disabled / greyed out | App is running on HTTP — HTTPS required for mic in production |
| `SarvamSTTError: 401` | Sarvam API key invalid or expired — check `dashboard.sarvam.ai` |
| `SarvamTTSError: 400` | Text may be too long or language code invalid |
| No audio playback | Browser may block autoplay — click a button first to unlock AudioContext |
| `Config error: missing SUPABASE_URL` | `.env` not loaded or variable name typo |
| `db: error` on health check | DB credentials wrong or schema not initialized |
| Empty results for "today" queries | Seed data dates may not match today — re-run `seed.sql` |
| CORS errors in browser | `ALLOWED_ORIGINS` doesn't include the frontend URL |
| SQL rejected as unsafe | Check `sql_validator.py` — legitimate new tables need allowlist update |
| Voice transcript is wrong language | Ensure language selector matches the language being spoken |
