# CLI Generation Prompt — Vaani AI Banking Data Assistant

> Copy the prompt block below into Claude (claude.ai) to generate the complete working
> project with all files, correct folder structure, Sarvam voice integration, and premium UI.

---

## How to Use

1. Open [claude.ai](https://claude.ai) (use Claude Sonnet or Opus for best results)
2. Copy everything between `---BEGIN PROMPT---` and `---END PROMPT---`
3. Paste as your message — Claude will generate all files
4. Save each file to its specified path
5. Follow `deploy.md` to configure credentials and launch

Or via API:
```bash
cat prompt.md | sed -n '/---BEGIN PROMPT---/,/---END PROMPT---/p' | \
  anthropic api messages create --model claude-sonnet-4-20250514 --max-tokens 8000
```

---

---BEGIN PROMPT---

You are a senior full-stack software engineer. Generate a complete, production-ready **Vaani — AI Banking Data Assistant** project. Output every file with its full path as a header (e.g. `### FILE: backend/main.py`) followed by the complete file contents in a code block. Do not omit any file. Do not use placeholder comments like "add logic here". Every function must be fully implemented.

## Project Identity

Product name: **Vaani** (Sanskrit for speech/voice)
Tagline: AI Banking Intelligence — Speak or Type to Query Your Data

## Tech Stack

- **Frontend**: Plain HTML5, CSS3, Vanilla JavaScript — NO frameworks, NO Streamlit, NO scaffolding
- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI — Text**: Anthropic Claude API (`claude-sonnet-4-20250514`)
- **AI — Voice STT**: Sarvam AI `saarika:v2` via `POST https://api.sarvam.ai/speech-to-text`
- **AI — Voice TTS**: Sarvam AI `bulbul:v1` via `POST https://api.sarvam.ai/text-to-speech`
- **Database**: Supabase PostgreSQL 15 — psycopg2 direct connection pool
- **Charts**: Chart.js 4.x via CDN

---

## Files to Generate — Complete List

Generate ALL files below with full implementations:

---

### 1. `supabase/schema.sql`
PostgreSQL schema with:
- `customers` (id SERIAL PK, name, email UNIQUE, phone, created_at TIMESTAMPTZ DEFAULT NOW())
- `accounts` (id SERIAL PK, customer_id FK→customers, account_number UNIQUE, account_type CHECK IN ('savings','current','fixed_deposit'), balance NUMERIC(15,2) DEFAULT 0, status CHECK IN ('active','inactive','frozen'), created_at)
- `transactions` (id SERIAL PK, account_id FK→accounts, transaction_type CHECK IN ('credit','debit'), amount NUMERIC(15,2) CHECK > 0, description TEXT, created_at)
- All foreign keys with ON DELETE CASCADE
- Indexes: transactions(account_id), transactions(created_at DESC), transactions(amount), accounts(customer_id), accounts(account_number)

---

### 2. `supabase/seed.sql`
Insert realistic data:
- 5 customers with Indian names (e.g. Arun Kumar, Priya Sharma)
- 10 accounts (mix of savings/current, spread across customers)
- 60 transactions: mix of credit/debit, varied amounts (some > 10,000 and > 50,000), dates spanning today, this week, and older dates
- Use `NOW()`, `NOW() - INTERVAL '1 day'`, `NOW() - INTERVAL '3 days'`, etc. for dates

---

### 3. `supabase/rls_policies.sql`
- Enable RLS on all three tables
- Create policy: allow SELECT for `service_role`
- Create read-only role `banking_readonly` with GRANT SELECT on all three tables

---

### 4. `backend/requirements.txt`
```
fastapi
uvicorn[standard]
psycopg2-binary
anthropic
python-dotenv
pydantic
pydantic-settings
python-multipart
httpx
```

---

### 5. `backend/config.py`
Pydantic BaseSettings loading these env vars (all required unless noted):
- `supabase_url`, `supabase_service_key`
- `supabase_db_host`, `supabase_db_port` (int), `supabase_db_name`, `supabase_db_user`, `supabase_db_password`
- `anthropic_api_key`
- `sarvam_api_key`
- `sarvam_stt_model` (default "saarika:v2")
- `sarvam_tts_model` (default "bulbul:v1")
- `sarvam_tts_voice` (default "meera")
- `allowed_origins` (default "*")
- `app_env` (default "development")

Export singleton `settings = Settings()`.

---

### 6. `backend/database/__init__.py` (empty)

### 7. `backend/database/connection.py`
- `DatabasePool` class using `psycopg2.pool.ThreadedConnectionPool(minconn=2, maxconn=10)`
- Connects using Supabase direct PostgreSQL credentials from `config.settings`
- `get_connection()` context manager — yields connection, puts back on exit
- `test_connection() -> bool`
- Module-level singleton `db_pool = DatabasePool()`

---

### 8. `backend/database/executor.py`
- Custom exception: `class QueryExecutionError(Exception): pass`
- `execute_query(sql: str) -> dict`:
  - Gets connection from pool
  - Sets `SET statement_timeout = '30000'`
  - Executes SQL with `cursor.execute(sql)`
  - Returns `{"columns": list[str], "rows": list[list], "count": int}`
  - On any exception: rollback, re-raise as `QueryExecutionError`

---

### 9. `backend/ai/__init__.py` (empty)

### 10. `backend/ai/prompt_builder.py`
- `build_system_prompt() -> str`
- Returns a detailed system prompt that includes:
  - Full schema (table names, columns, types, foreign key relationships)
  - Current date AND time (use `datetime.now()` with formatted string)
  - Strict rule: respond with ONLY one valid PostgreSQL SELECT statement. No markdown. No explanation. No semicolons at end. No LIMIT unless user asks for it.
  - Three example pairs (natural language → correct SQL) showing proper JOINs:
    1. Customers who transacted above 50000 this week → multi-table JOIN with date filter
    2. Last 10 transactions above 10000 → ORDER BY created_at DESC LIMIT 10
    3. Total credit transactions today → SUM with DATE filter

---

### 11. `backend/ai/claude_client.py`
- `generate_sql(query: str) -> str`:
  - Calls Anthropic API with model `claude-sonnet-4-20250514`, max_tokens=500, temperature=0
  - System prompt from `prompt_builder.build_system_prompt()`
  - User message: the natural language query
  - Extracts `.content[0].text`
  - Strips ```sql / ``` fences if present
  - Strips whitespace
  - Returns clean SQL string

---

### 12. `backend/voice/__init__.py` (empty)

### 13. `backend/voice/sarvam_stt.py`
- Custom exception: `class SarvamSTTError(Exception): pass`
- `transcribe(audio_bytes: bytes, language_code: str = "en-IN") -> str`:
  - Calls `POST https://api.sarvam.ai/speech-to-text` using `httpx`
  - Multipart form: `file=("audio.webm", audio_bytes, "audio/webm")`, `model=settings.sarvam_stt_model`, `language_code=language_code`
  - Header: `api-subscription-key: settings.sarvam_api_key`
  - On 200: return `response_json["transcript"]`
  - On non-200: raise `SarvamSTTError(f"STT failed: {status} {body}")`

---

### 14. `backend/voice/sarvam_tts.py`
- Custom exception: `class SarvamTTSError(Exception): pass`
- `synthesize(text: str, language_code: str = "en-IN") -> bytes`:
  - Calls `POST https://api.sarvam.ai/text-to-speech` using `httpx`
  - JSON body: `{"inputs": [text], "target_language_code": language_code, "speaker": settings.sarvam_tts_voice, "model": settings.sarvam_tts_model, "enable_preprocessing": true}`
  - Header: `api-subscription-key: settings.sarvam_api_key`, `Content-Type: application/json`
  - On 200: base64-decode `response_json["audios"][0]`, return bytes
  - On non-200: raise `SarvamTTSError(f"TTS failed: {status} {body}")`

---

### 15. `backend/voice/summary_builder.py`
- `build_summary(query: str, columns: list, rows: list, count: int) -> str`:
  - If count == 0: return `"No results found for your query."`
  - If count == 1 and columns contains "sum" or "total" or "count": return `"The result is {rows[0][0]}."`
  - For transaction lists: `"Found {count} transactions."` + if amount column exists: `" The highest amount is ₹{max_amount:,.0f}."`
  - For customer/account lists: `"Found {count} records."` + first result name if available
  - Keep output under 280 characters total

---

### 16. `backend/validators/__init__.py` (empty)

### 17. `backend/validators/sql_validator.py`
- `validate_sql(sql: str) -> tuple[bool, str | None]`
- Sequential checks:
  1. Not empty → (False, "empty_query")
  2. Starts with SELECT (case-insensitive) → (False, "not_select")
  3. Blocklist (case-insensitive): INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, EXEC, EXECUTE, GRANT, REVOKE, xp_ → (False, "forbidden_keyword:{keyword}")
  4. No semicolons except optionally at very end → (False, "mid_query_semicolon")
  5. Table allowlist: scan for table names after FROM and JOIN — only customers, accounts, transactions allowed → (False, "disallowed_table:{name}")
  6. Length ≤ 2000 → (False, "query_too_long")
  7. All pass → (True, None)

---

### 18. `backend/api/__init__.py` (empty)

### 19. `backend/api/models.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Any

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)

class SpeakRequest(BaseModel):
    text: str = Field(..., max_length=300)
    language_code: str = "en-IN"

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str] = None
    columns: List[str] = []
    rows: List[List[Any]] = []
    count: int = 0
    summary: Optional[str] = None
    error: Optional[str] = None
```

---

### 20. `backend/api/routes.py`
Implement an `APIRouter` with these four routes:

**`POST /api/query`** (accepts `QueryRequest`, returns `QueryResponse`):
1. Call `claude_client.generate_sql(request.query)`
2. Call `sql_validator.validate_sql(sql)` — if invalid return `QueryResponse(success=False, error=reason)`
3. Call `executor.execute_query(sql)`
4. Build summary with `summary_builder.build_summary(...)`
5. Return `QueryResponse(success=True, sql=sql, summary=summary, ...)`
6. On any exception: return `QueryResponse(success=False, error="An error occurred. Please try again.")`

**`POST /api/voice/transcribe`** (accepts multipart: `audio` file + `language_code` form field):
1. Read audio bytes from uploaded file
2. Call `sarvam_stt.transcribe(audio_bytes, language_code)`
3. Run the transcribed text through the same pipeline as `/api/query`
4. Return `QueryResponse` with summary populated

**`POST /api/voice/speak`** (accepts `SpeakRequest`, returns audio):
1. Call `sarvam_tts.synthesize(request.text, request.language_code)`
2. Return `StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/wav")`
3. On `SarvamTTSError`: return HTTP 502 with JSON error

**`GET /api/health`**:
- Test DB: call `db_pool.test_connection()`
- Test Sarvam: HEAD request to `https://api.sarvam.ai` (just connectivity check)
- Return `{"status": "ok", "db": "connected"|"error", "sarvam": "reachable"|"unreachable"}`

---

### 21. `backend/main.py`
FastAPI app:
- `CORSMiddleware` with `settings.allowed_origins` (split by comma), all methods, all headers
- Include router from `api/routes.py`
- `@app.on_event("startup")`: log "Vaani Banking Assistant started — ENV: {settings.app_env}"
- Generic exception handler: return `{"success": false, "error": "Internal server error"}` — never expose stack trace

---

### 22. `frontend/css/styles.css`
Full custom dark luxury CSS. Requirements:

**CSS Variables (`:root`)**:
- `--bg-void: #050810`, `--bg-deep: #080d1a`, `--bg-panel: #0d1526`, `--bg-card: #111e35`, `--bg-lift: #162338`, `--bg-hover: #1c2c45`
- `--accent-gold: #d4a853`, `--accent-gold-dim: #9a7a3a`, `--accent-gold-glow: rgba(212,168,83,0.15)`
- `--accent-teal: #2dd4bf`, `--accent-teal-glow: rgba(45,212,191,0.12)`
- `--text-primary: #f0ece3`, `--text-secondary: #8b98b4`, `--text-muted: #4a5578`
- `--font-display: 'Instrument Serif', serif`, `--font-ui: 'Syne', sans-serif`, `--font-mono: 'JetBrains Mono', monospace`

**Layout**: CSS Grid — `grid-template-areas: "header header" "sidebar main"`. Sidebar 280px fixed. Header 64px fixed.

**Background FX**: `body::before` with CSS grid-line overlay (`background-image` with linear-gradient lines, `background-size: 40px 40px`, very subtle opacity 0.03). Two `.orb` divs with `position:fixed`, `filter:blur(120px)`, pointer-events:none.

**Header**: frosted glass — `background: rgba(5,8,16,0.85)`, `backdrop-filter: blur(20px)`, `border-bottom: 1px solid rgba(255,255,255,0.05)`. Logo mark is a 36×36px gold gradient rounded square. Brand name in `var(--font-display)` italic.

**Sidebar**: `background: var(--bg-deep)`, `border-right: 1px solid rgba(255,255,255,0.05)`. History items are clickable pills with hover glow.

**Query panel**: textarea with `background: var(--bg-card)`, `border: 1px solid rgba(255,255,255,0.08)`, gold glow on focus (`box-shadow: 0 0 0 2px var(--accent-gold-glow)`), `font-family: var(--font-ui)`, min-height 80px, resize vertical.

**Submit button**: gold gradient background, `font-family: var(--font-ui)`, `font-weight: 600`, hover scale(1.02), active scale(0.98).

**Mic button**: circular, 48×48px, `background: var(--bg-lift)`, gold border. When `.recording`: red background + CSS `@keyframes pulse-ring` that expands and fades a ring outward. Transition all states.

**Language selector**: styled `<select>` matching dark theme, gold border on focus.

**Results table**: `border-collapse: collapse`, sticky `<thead>` with `background: var(--bg-panel)`. `<th>` in uppercase 11px tracked gold text. `<tr>:hover` gold-tinted background. Alternating `<tr>:nth-child(even)` subtle tint. Sortable headers show ↑↓ arrows.

**SQL display**: `font-family: var(--font-mono)`, `background: #020509`, `border: 1px solid var(--accent-gold-dim)`, `border-radius: 8px`, `color: var(--accent-teal)`, collapsible.

**Chart container**: `background: var(--bg-panel)`, border, border-radius 12px, padding 24px.

**Animations**:
- `@keyframes fade-up`: opacity 0→1, translateY 20px→0, used for page load stagger
- `@keyframes pulse-ring`: scale + opacity for mic recording state
- `@keyframes pulse-dot`: subtle scale for status dot
- Row entry: each `<tr>` gets `animation: fade-up 0.3s ease forwards` with staggered `animation-delay`

**Toast**: fixed bottom-right, `background: var(--bg-card)`, colored left border (teal=success, red=error), slide-in animation.

**Status dot**: 8px circle, green when connected, red on error, animated pulse.

Import Google Fonts in CSS: `@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Syne:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');`

---

### 23. `frontend/js/api.js`
```javascript
const API_BASE_URL = 'http://localhost:8000';

async function queryAssistant(query) { ... }
// POST /api/query with {query}
// Returns parsed QueryResponse
// Throws on network error or non-2xx

async function transcribeAndQuery(audioBlob, languageCode) { ... }
// POST /api/voice/transcribe multipart (audio file + language_code)
// Returns parsed QueryResponse

async function speakSummary(text, languageCode) { ... }
// POST /api/voice/speak with {text, language_code}
// Returns audio blob (type: audio/wav)

async function checkHealth() { ... }
// GET /api/health → returns health object
```

---

### 24. `frontend/js/voice.js`
Full voice state machine:

```javascript
// State: 'idle' | 'recording' | 'processing'
let mediaRecorder, audioChunks = [], currentState = 'idle';

async function startRecording() {
  // navigator.mediaDevices.getUserMedia({audio: true})
  // Create MediaRecorder, collect chunks on dataavailable
  // Update mic button UI to recording state
}

function stopRecording() {
  // Stop MediaRecorder
  // Collect chunks into Blob
  // Return blob
}

async function handleVoiceQuery(languageCode) {
  // startRecording → wait for user to stop (button click) → stopRecording
  // Call transcribeAndQuery(blob, languageCode) from api.js
  // On success: populate textarea with transcript, render results
  // On error: showToast('Voice query failed', 'error')
}

function playAudioBlob(blob) {
  // AudioContext + decodeAudioData + start source
}

function isMicAvailable() {
  // Returns true only if location.protocol === 'https:' || location.hostname === 'localhost'
}
```

Expose: `initVoice()` — called on DOMContentLoaded. If `!isMicAvailable()`, disable mic button and show tooltip "Mic requires HTTPS".

---

### 25. `frontend/js/charts.js`
```javascript
let currentChart = null;

function detectChartType(columns, rows) {
  // Returns 'bar' | 'line' | 'bignumber' | 'none'
  // bar: 2 cols, col2 is numeric
  // line: col1 looks like date (contains '-' and is parseable), col2 numeric
  // bignumber: 1 row, 1 col, numeric
  // none: otherwise
}

function renderChart(canvasId, columns, rows) {
  // Destroy currentChart if exists
  // Detect type
  // If 'none': hide chart container
  // Chart.js config with custom colors:
  //   backgroundColor: 'rgba(212,168,83,0.2)', borderColor: '#d4a853' for bar
  //   backgroundColor: 'rgba(45,212,191,0.1)', borderColor: '#2dd4bf' for line
  //   Chart options: dark grid lines (rgba(255,255,255,0.05)), white-ish tick labels
  // If 'bignumber': render a styled div, not a canvas
}
```

---

### 26. `frontend/js/app.js`
Full application orchestration:

```javascript
// DOMContentLoaded:
//   1. checkHealth() → update status dot (green/red) + sarvam status
//   2. loadHistory() from localStorage
//   3. initVoice()
//   4. bind submit button + Ctrl+Enter on textarea

async function submitQuery(queryText) {
  if (!queryText.trim()) return;
  showLoading();
  try {
    const res = await queryAssistant(queryText);
    if (res.success) {
      renderSQL(res.sql);
      renderTable(res.columns, res.rows);
      renderChart('chart-canvas', res.columns, res.rows);
      updateRowCount(res.count);
      showResultsPanel();
      addToHistory(queryText);
      if (res.summary) setupTTSButton(res.summary);
    } else {
      showToast(res.error || 'Query failed', 'error');
    }
  } catch (e) {
    showToast('Connection error. Is the backend running?', 'error');
  } finally {
    hideLoading();
  }
}

function renderTable(columns, rows) {
  // Build <table> with <thead> (sortable) and <tbody>
  // Each <tr> gets animation-delay based on index for stagger effect
  // Clicking <th> toggles sort asc/desc on that column
}

function renderSQL(sql) {
  // Show SQL in the collapsible code block
  // Syntax highlight: keywords (SELECT, FROM, WHERE, JOIN, etc.) wrapped in <span class="kw">
}

function addToHistory(query) {
  // Save to localStorage array (max 10, newest first)
  // Re-render history list — each item is a clickable pill
}

function setupTTSButton(summary) {
  // Show "🔊 Hear summary" button
  // On click: call speakSummary(summary, currentLanguageCode)
  //           → get audio blob → playAudioBlob(blob)
}

function showToast(msg, type) { ... }  // type: 'success'|'error'
function showLoading() { ... }
function hideLoading() { ... }
function showResultsPanel() { ... }
function toggleSQL() { ... }          // collapse/expand SQL block
```

---

### 27. `frontend/index.html`
Complete single-page HTML. Must include:

**Head**: charset, viewport, title "Vaani — AI Banking Intelligence", Google Fonts import (Instrument Serif, Syne, JetBrains Mono), Chart.js CDN (`https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js`), `styles.css`.

**Body structure**:
```
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>

<div class="app">
  <header>
    <div class="logo">
      <div class="logo-mark">⬡</div>
      <div>
        <span class="brand-name">Vaani</span>
        <span class="brand-tag">AI Banking Intelligence</span>
      </div>
    </div>
    <div class="header-right">
      <select id="language-select"><!-- 11 Sarvam language options --></select>
      <div class="status-pill">
        <div class="status-dot" id="status-dot"></div>
        <span id="status-text">Connecting...</span>
      </div>
    </div>
  </header>

  <aside class="sidebar">
    <div class="sidebar-header">Query History</div>
    <ul id="history-list"></ul>
  </aside>

  <main class="main-panel">
    <div class="query-section">
      <h1 class="query-title">Ask your banking data<span class="cursor">_</span></h1>
      <p class="query-hint">Type a question or click the mic to speak — in English or any Indian language</p>
      <div class="input-row">
        <textarea id="query-input" placeholder="e.g. Show last 10 transactions above ₹10,000..."></textarea>
        <button id="mic-btn" title="Voice query">🎙</button>
      </div>
      <div class="action-row">
        <button id="submit-btn">Ask Vaani</button>
        <span class="kbd-hint">or press Ctrl + Enter</span>
      </div>
    </div>

    <div class="results-section" id="results-section" style="display:none">
      <div class="results-header">
        <div class="sql-toggle" onclick="toggleSQL()">
          <span class="sql-badge">SQL</span>
          <span id="sql-toggle-icon">▼</span>
        </div>
        <div class="row-count" id="row-count"></div>
        <button id="tts-btn" style="display:none">🔊 Hear summary</button>
      </div>
      <pre id="sql-display" class="sql-display"></pre>
      <div class="chart-container" id="chart-container" style="display:none">
        <canvas id="chart-canvas"></canvas>
      </div>
      <div id="table-container"></div>
    </div>

    <div class="loading-overlay" id="loading" style="display:none">
      <div class="spinner"></div>
      <p class="loading-text">Thinking...</p>
    </div>
  </main>
</div>

<div id="toast" class="toast"></div>
```

Script tags at end of body (in order): `api.js`, `charts.js`, `voice.js`, `app.js`.

---

### 28. `.env.example`
```
SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_DB_HOST=db.YOUR_PROJECT_REF.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-database-password

ANTHROPIC_API_KEY=sk-ant-your-key

SARVAM_API_KEY=your-sarvam-api-key
SARVAM_STT_MODEL=saarika:v2
SARVAM_TTS_MODEL=bulbul:v1
SARVAM_TTS_VOICE=meera

ALLOWED_ORIGINS=http://localhost:3000
APP_ENV=development
```

---

### 29. `.gitignore`
```
.env
__pycache__/
*.pyc
*.pyo
venv/
.venv/
*.egg-info/
dist/
build/
.DS_Store
*.log
node_modules/
.idea/
.vscode/
```

---

## Output Rules

- Every file path as `### FILE: path/to/file`
- Complete implementation — no `...`, no "rest of code here"
- All Python files: correct imports at top
- All `__init__.py` files included (even if empty)
- Frontend works by opening `index.html` directly in browser (no build step)
- Backend starts with `uvicorn main:app --reload` from `backend/` directory
- No test files, no CI/CD configs, no Docker unless listed above

Generate all 29 files now.

---END PROMPT---

---

## Expected Output — 29 Files

```
supabase/schema.sql
supabase/seed.sql
supabase/rls_policies.sql
backend/requirements.txt
backend/config.py
backend/main.py
backend/database/__init__.py
backend/database/connection.py
backend/database/executor.py
backend/ai/__init__.py
backend/ai/prompt_builder.py
backend/ai/claude_client.py
backend/voice/__init__.py
backend/voice/sarvam_stt.py
backend/voice/sarvam_tts.py
backend/voice/summary_builder.py
backend/validators/__init__.py
backend/validators/sql_validator.py
backend/api/__init__.py
backend/api/models.py
backend/api/routes.py
frontend/index.html
frontend/css/styles.css
frontend/js/api.js
frontend/js/voice.js
frontend/js/charts.js
frontend/js/app.js
.env.example
.gitignore
```

## After Generation

```bash
mkdir -p vaani-banking-assistant/{supabase,backend/{database,ai,voice,validators,api},frontend/{css,js}}
cd vaani-banking-assistant
# Save each file to its path, then follow deploy.md
```

## If Output Truncates

Break into two runs:
- **Run 1**: "Generate files 1–15 from the Vaani project prompt" (supabase + backend)
- **Run 2**: "Generate files 16–29 from the Vaani project prompt" (frontend + config)

Or re-request individual files: "Generate only `backend/voice/sarvam_stt.py` — complete, no placeholders."
