# Technical Specification — Vaani AI Banking Data Assistant

## 1. Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (User)                            │
│                                                                  │
│  index.html · styles.css · app.js · api.js · voice.js           │
│                                                                  │
│  [Text Input] ──────────────────────────────────────────┐        │
│  [Mic Button] → MediaRecorder → WebM blob ──────────────┤        │
│                                                          │        │
│  Result: Table render + Chart.js + TTS audio playback   │        │
└──────────────────────────────────│──────────────────────┘        │
                                   │ HTTP (JSON / multipart)
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Python 3.11)                   │
│                                                                  │
│  POST /api/query                                                 │
│    └─► prompt_builder → claude_client → sql_validator → executor │
│                                                                  │
│  POST /api/voice/transcribe                                      │
│    └─► sarvam_stt → transcribed text → same SQL pipeline        │
│                                                                  │
│  POST /api/voice/speak                                           │
│    └─► summary_builder → sarvam_tts → audio bytes response      │
│                                                                  │
│  GET  /api/health                                                │
│    └─► db connection test → {"status":"ok","db":"connected"}     │
└──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  External APIs                                                   │
│  ├─ Anthropic Claude  api.anthropic.com/v1/messages              │
│  ├─ Sarvam STT        api.sarvam.ai/speech-to-text              │
│  └─ Sarvam TTS        api.sarvam.ai/text-to-speech              │
└──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│  Supabase (PostgreSQL 15)                                        │
│  Tables: customers · accounts · transactions                     │
│  RLS: SELECT-only service role enforced                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Database Schema

### 2.1 `customers`

```sql
CREATE TABLE customers (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) UNIQUE NOT NULL,
    phone      VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.2 `accounts`

```sql
CREATE TABLE accounts (
    id             SERIAL PRIMARY KEY,
    customer_id    INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type   VARCHAR(50) NOT NULL CHECK (account_type IN ('savings','current','fixed_deposit')),
    balance        NUMERIC(15,2) NOT NULL DEFAULT 0.00,
    status         VARCHAR(20) NOT NULL DEFAULT 'active'
                   CHECK (status IN ('active','inactive','frozen')),
    created_at     TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.3 `transactions`

```sql
CREATE TABLE transactions (
    id               SERIAL PRIMARY KEY,
    account_id       INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('credit','debit')),
    amount           NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    description      TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.4 Indexes

```sql
CREATE INDEX idx_txn_account_id  ON transactions(account_id);
CREATE INDEX idx_txn_created_at  ON transactions(created_at DESC);
CREATE INDEX idx_txn_amount      ON transactions(amount);
CREATE INDEX idx_acc_customer_id ON accounts(customer_id);
CREATE INDEX idx_acc_number      ON accounts(account_number);
```

---

## 3. Backend Specification

### 3.1 `config.py`

Uses `pydantic-settings` `BaseSettings`. Raises `ValidationError` at startup if any required variable is missing.

```
Required:
  SUPABASE_URL            Supabase project REST URL
  SUPABASE_SERVICE_KEY    service_role API key
  SUPABASE_DB_HOST        PostgreSQL host
  SUPABASE_DB_PORT        5432
  SUPABASE_DB_NAME        postgres
  SUPABASE_DB_USER        postgres
  SUPABASE_DB_PASSWORD    database password
  ANTHROPIC_API_KEY       Claude API key
  SARVAM_API_KEY          Sarvam AI API key
  ALLOWED_ORIGINS         comma-separated CORS origins
  APP_ENV                 development | production
```

### 3.2 `database/connection.py`

- `psycopg2.pool.ThreadedConnectionPool` — `minconn=2`, `maxconn=10`
- `get_connection()` — context manager; returns connection, puts it back on exit
- `test_connection()` — returns `True/False`; used by health endpoint

### 3.3 `database/executor.py`

`execute_query(sql: str) -> dict`

- Gets pooled connection
- Sets `statement_timeout = 30000` (30s)
- Executes query with cursor
- Returns `{"columns": list[str], "rows": list[list], "count": int}`
- Raises `QueryExecutionError` on any failure

### 3.4 `ai/prompt_builder.py`

`build_system_prompt() -> str`

System prompt contents:
- Full schema (all 3 tables, columns, types, FK relationships)
- Current date + time injected with `datetime.now()` (for "today", "this week" queries)
- Instruction: return **only** a valid PostgreSQL `SELECT` statement — no markdown, no explanation, no trailing semicolon
- 3 worked JOIN examples:
  - Customers who transacted above 50,000 this week → multi-table JOIN
  - Last 10 transactions above 10,000 → filtered `ORDER BY … LIMIT`
  - Total credits today → `SUM` + `DATE()` filter

### 3.5 `ai/claude_client.py`

`generate_sql(query: str) -> str`

```python
model        = "claude-sonnet-4-20250514"
max_tokens   = 500
temperature  = 0          # deterministic SQL generation
```

- Builds system prompt → sends user query
- Extracts text from `content[0].text`
- Strips markdown fences (` ```sql `, ` ``` `)
- Strips whitespace
- Returns raw SQL string

### 3.6 `voice/sarvam_stt.py`

`transcribe(audio_bytes: bytes, language_code: str) -> str`

```
POST https://api.sarvam.ai/speech-to-text
Headers:
  api-subscription-key: {SARVAM_API_KEY}
Body (multipart/form-data):
  file:     audio blob (WebM/opus)
  model:    saarika:v2
  language_code: {language_code}   e.g. "en-IN", "hi-IN"
Returns:
  transcript string from response JSON
```

Raises `SarvamSTTError` on non-200 responses.

### 3.7 `voice/sarvam_tts.py`

`synthesize(text: str, language_code: str) -> bytes`

```
POST https://api.sarvam.ai/text-to-speech
Headers:
  api-subscription-key: {SARVAM_API_KEY}
  Content-Type: application/json
Body:
  {
    "inputs": ["{text}"],
    "target_language_code": "{language_code}",
    "model": "bulbul:v1",
    "enable_preprocessing": true
  }
Returns:
  audio bytes (WAV)
```

Raises `SarvamTTSError` on non-200 responses.

### 3.8 `voice/summary_builder.py`

`build_summary(query: str, columns: list, rows: list, count: int) -> str`

Builds a short, speakable English summary:
- `"Found {count} results."` for list queries
- `"The total is ₹{value}."` for single-aggregate queries
- `"Top result: {col1} is {val1}, {col2} is {val2}."` for multi-column single rows
- Caps at 3 sentences to keep TTS audio under 10 seconds

### 3.9 `validators/sql_validator.py`

`validate_sql(sql: str) -> tuple[bool, str | None]`

Sequential validation pipeline — all steps must pass:

| Step | Check | Reject reason |
|------|-------|--------------|
| 1 | Not empty after strip | "Empty query" |
| 2 | Starts with `SELECT` (case-insensitive) | "Only SELECT is allowed" |
| 3 | Blocklist: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `EXEC`, `EXECUTE`, `xp_`, `GRANT`, `REVOKE` | "Unsafe operation detected" |
| 4 | No semicolons except optionally at the very end | "Multiple statements not allowed" |
| 5 | Table allowlist — only `customers`, `accounts`, `transactions` referenced in `FROM`/`JOIN` clauses | "Unauthorized table reference" |
| 6 | Max length 2000 chars | "Query too long" |

Returns `(True, None)` on pass, `(False, reason)` on first failure.

### 3.10 `api/models.py`

```python
class QueryRequest(BaseModel):
    query: str      # min_length=3, max_length=500

class VoiceTranscribeRequest(BaseModel):
    language_code: str = "en-IN"

class VoiceSpeakRequest(BaseModel):
    text: str           # max_length=1000
    language_code: str = "en-IN"

class QueryResponse(BaseModel):
    success: bool
    sql: Optional[str]
    columns: List[str]
    rows: List[List[Any]]
    count: int
    summary: Optional[str]   # speakable summary string
    error: Optional[str]
```

### 3.11 `api/routes.py` — Route Table

| Method | Path | Input | Output | Description |
|--------|------|-------|--------|-------------|
| `POST` | `/api/query` | `QueryRequest` JSON | `QueryResponse` JSON | Text query → SQL → results |
| `POST` | `/api/voice/transcribe` | `multipart/form-data` (audio file + language_code) | `{"transcript": str}` | Audio → Sarvam STT → text |
| `POST` | `/api/voice/speak` | `VoiceSpeakRequest` JSON | `audio/wav` bytes | Text → Sarvam TTS → audio |
| `GET` | `/api/health` | — | `{"status":"ok","db":"connected"\|"error"}` | Health check |

**`POST /api/query` flow:**
1. Validate `QueryRequest` (Pydantic)
2. `prompt_builder.build_system_prompt()` + `claude_client.generate_sql(query)`
3. `sql_validator.validate_sql(sql)` — if invalid → return `QueryResponse(success=False, error=reason)`
4. `executor.execute_query(sql)` → columns, rows, count
5. `summary_builder.build_summary(...)` → summary string
6. Return `QueryResponse(success=True, ...)`

**`POST /api/voice/transcribe` flow:**
1. Extract audio bytes from multipart form
2. Get `language_code` field (default `en-IN`)
3. `sarvam_stt.transcribe(audio_bytes, language_code)` → transcript
4. Return `{"transcript": transcript}`

**`POST /api/voice/speak` flow:**
1. Validate `VoiceSpeakRequest`
2. `sarvam_tts.synthesize(text, language_code)` → audio bytes
3. Return `Response(content=audio_bytes, media_type="audio/wav")`

### 3.12 `main.py`

```python
app = FastAPI(title="Vaani AI Banking Assistant")
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, ...)
app.include_router(router)

@app.on_event("startup")
async def startup():
    logger.info("Vaani AI Banking Assistant started")
    # warm DB pool

@app.exception_handler(Exception)
async def global_error_handler(req, exc):
    return JSONResponse({"error": "An unexpected error occurred."}, status_code=500)
```

---

## 4. Frontend Specification

### 4.1 Design Tokens — `styles.css`

```css
:root {
  --bg-void:       #050810;    /* page background */
  --bg-deep:       #080d1a;
  --bg-panel:      #0d1526;    /* sidebar */
  --bg-card:       #111e35;    /* cards */
  --bg-lift:       #162338;    /* elevated elements */
  --bg-hover:      #1c2c45;

  --accent-gold:   #d4a853;    /* primary accent */
  --accent-teal:   #2dd4bf;    /* secondary accent */
  --accent-green:  #22c55e;    /* status: connected */
  --accent-red:    #ef4444;    /* status: error */

  --text-primary:  #f0ece3;
  --text-secondary:#8b98b4;
  --text-muted:    #4a5578;

  --border-subtle: rgba(255,255,255,0.05);
  --border-gold:   rgba(212,168,83,0.3);

  --font-display:  'Instrument Serif', Georgia, serif;
  --font-ui:       'Syne', sans-serif;
  --font-mono:     'JetBrains Mono', monospace;
}
```

Background effects: CSS `background-image` grid lines + two fixed `filter: blur(120px)` orbs for depth.

### 4.2 `voice.js` — Voice Flow

```javascript
// State
let mediaRecorder = null;
let audioChunks   = [];
let isRecording   = false;

async function startRecording() {
  // 1. getUserMedia({ audio: true })
  // 2. MediaRecorder(stream, { mimeType: 'audio/webm' })
  // 3. Collect chunks on dataavailable
  // 4. Start waveform animation
  // 5. Animate mic button: add .recording class (pulse-ring)
}

async function stopRecording() {
  // 1. mediaRecorder.stop() → onstop builds Blob
  // 2. POST blob + language_code to /api/voice/transcribe (multipart)
  // 3. Receive transcript → populate textarea
  // 4. Auto-submit query
  // 5. Stop waveform animation
}

async function speakSummary(summaryText, languageCode) {
  // 1. POST { text, language_code } to /api/voice/speak
  // 2. Receive audio/wav bytes
  // 3. AudioContext.decodeAudioData → play via AudioBufferSourceNode
}
```

**Waveform animation:** 5 `<div class="bar">` elements animated with staggered `animation-delay` using `@keyframes wave` (height oscillates 4px → 20px).

**Mic button states:**

| State | CSS class | Visual |
|-------|-----------|--------|
| Idle | `.mic-btn` | Gold ring, mic icon |
| Recording | `.mic-btn.recording` | Pulsing gold ring + red dot |
| Processing | `.mic-btn.processing` | Spinning border |

### 4.3 `charts.js` — Auto-Detection

`renderChart(containerId, columns, rows) → void`

| Condition | Chart Type |
|-----------|-----------|
| 1 row, 1 numeric column | Big-number card with label |
| 2 columns: string + numeric | Horizontal bar chart |
| 2 columns: date/time + numeric | Line chart |
| 3+ columns or no clear pattern | No chart (table only) |

Destroys previous Chart.js instance before rendering new one. Uses:
- Bar color: `rgba(45, 212, 191, 0.7)` (teal)
- Line color: `#d4a853` (gold)
- Grid color: `rgba(255,255,255,0.05)`
- Tick color: `#8b98b4`

### 4.4 `app.js` — Core Logic

- `initApp()` — health check → update status pill → load history from localStorage
- `submitQuery(text)` — `showLoading()` → `api.queryAssistant()` → `renderResults()` → `hideLoading()`
- `renderResults(response)` — populate SQL box, row count badge, call `renderTable()`, call `renderChart()`
- `renderTable(columns, rows)` — build `<table>` with `<th>` click-to-sort; ascending/descending toggle
- `addToHistory(query)` — push to array (max 10), persist to `localStorage`, re-render sidebar list
- `showLoading()` / `hideLoading()` — toggle spinner overlay, disable submit and mic buttons
- `showToast(message, type)` — show toast div, auto-dismiss after 3s

### 4.5 `index.html` — Structure

```
<head>
  Google Fonts: Instrument Serif, Syne, JetBrains Mono
  Chart.js 4.x CDN
  styles.css

<body>
  .orb.orb-1   (gold glow, top-right)
  .orb.orb-2   (teal glow, bottom-left)

  .app  (grid: header / sidebar / main)
    <header>
      .logo  (mark + "Vaani" italic + "AI BANKING" tag)
      .header-right  (status pill + language dropdown)

    <aside.sidebar>
      "Query History" heading
      <ul#history-list>

    <main>
      .query-panel
        <textarea#query-input>
        .query-controls
          <button#mic-btn>  (waveform bars inside)
          <select#lang-select>  (11 Sarvam languages)
          <button#submit-btn>
        .keyboard-hint  "Ctrl+Enter to submit"

      .results-panel  (hidden until first result)
        .sql-header  (badge + toggle button)
        .sql-box  (monospace, collapsible)
        .result-meta  (row count badge + speak button)
        .chart-container  (<canvas#result-chart>)
        .table-container  (<table#result-table>)

      .loading-overlay  (spinner, hidden by default)

  .toast#toast  (success / error auto-dismiss)

  <script> api.js, voice.js, charts.js, app.js
```

---

## 5. Security Specification

| Control | Implementation |
|---------|---------------|
| SQL allowlist | 6-step `sql_validator.py` — all mutations blocked before execution |
| Read-only DB | Supabase service role: `GRANT SELECT` only |
| No interpolation | Claude generates SQL from natural language — no user string in SQL |
| Sarvam key | Server-side env var only — never sent to browser |
| Audio discard | Audio bytes processed in memory and not persisted |
| CORS | `ALLOWED_ORIGINS` env var — locked down in production |
| Error sanitization | `global_error_handler` returns generic message — no stack trace |
| Query timeout | `statement_timeout = 30000ms` per DB connection |
| Input limits | NL query: max 500 chars; TTS text: max 1000 chars |
| HTTPS required | Documented constraint — mic unavailable on plain HTTP |

---

## 6. Environment Variables

```env
# Supabase
SUPABASE_URL=https://YOUR_REF.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DB_HOST=db.YOUR_REF.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-db-password

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Sarvam AI
SARVAM_API_KEY=your-sarvam-api-key

# App
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
APP_ENV=production
```

---

## 7. Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Text query response | p95 < 5 seconds |
| Voice round-trip (STT + query + TTS) | p95 < 8 seconds |
| Concurrent users | 20 simultaneous without degradation |
| SQL safety | 100% of mutating queries blocked |
| Uptime | 99.5% (excluding Supabase / Anthropic / Sarvam outages) |
| Error rate | < 1% for valid queries |
| Unit test coverage | Core validator + executor ≥ 80% |
| UI load time | < 2 seconds (no build step, CDN-only assets) |
