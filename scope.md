# Scope — Vaani AI Banking Data Assistant

## Project Purpose

Deliver a production-grade AI banking assistant that enables non-technical banking business users to retrieve operational and transactional data from a structured relational database — by **typing or speaking** in English or Indian languages — without writing SQL or depending on engineering teams. The interface must be a premium, visually distinctive dark dashboard built entirely from scratch with custom design.

---

## In Scope

### Functional Scope

| # | Feature | Description |
|---|---------|-------------|
| 1 | Text query input | Styled textarea with placeholder examples |
| 2 | **Voice query input — Sarvam STT** | Mic button captures audio; Sarvam `saarika:v2` transcribes to text |
| 3 | **Multilingual voice support** | 11 Indian languages + English via language selector dropdown |
| 4 | AI-to-SQL translation | Claude API converts query to validated PostgreSQL SELECT |
| 5 | Relational data retrieval | Queries across Customers → Accounts → Transactions with correct JOINs |
| 6 | Structured JSON response | Backend returns consistent typed JSON for every query |
| 7 | Tabular result display | Sortable, column-click HTML table in premium dark theme |
| 8 | Chart visualizations | Auto-detected bar / line / big-number via Chart.js 4.x |
| 9 | **Voice result readback — Sarvam TTS** | Result summary spoken aloud via `bulbul:v1` |
| 10 | Query history (session) | Last 10 queries in sidebar, clickable to re-run |
| 11 | Error feedback | Graceful user-facing messages — no stack traces exposed |
| 12 | Read-only SQL enforcement | All non-SELECT blocked at application layer |
| 13 | Health check endpoint | `/api/health` returns DB connectivity status |
| 14 | **Premium dark UI** | Fully custom luxury dashboard — navy/gold, glassmorphism cards |
| 15 | **Animated voice UI** | Pulse-ring mic button + live waveform bars during recording |
| 16 | SQL transparency | Generated SQL shown in collapsible monospace box |
| 17 | Keyboard shortcut | `Ctrl+Enter` submits query without mouse |

### Voice Scope — Sarvam AI

| Component | Detail |
|-----------|--------|
| STT model | `saarika:v2` via `POST https://api.sarvam.ai/speech-to-text` |
| TTS model | `bulbul:v1` via `POST https://api.sarvam.ai/text-to-speech` |
| Audio capture | Browser `MediaRecorder` API → WebM/opus blob |
| Audio playback | Web Audio API in browser |
| Language selector | `en-IN`, `hi-IN`, `ta-IN`, `te-IN`, `kn-IN`, `bn-IN`, `mr-IN`, `gu-IN`, `ml-IN`, `or-IN`, `pa-IN` |
| TTS summary | Built from query result — row count, key values, totals |
| Key storage | Sarvam API key on server only — never exposed to client |

### UI Design Scope

| Element | Specification |
|---------|--------------|
| Theme | Deep navy `#050810` background, liquid gold `#d4a853` accent, teal `#2dd4bf` secondary |
| Background | CSS grid lines + fixed blur orbs for depth |
| Cards | Glassmorphism — `backdrop-filter: blur` + gold border |
| Display font | Instrument Serif (italic, editorial) |
| UI font | Syne (geometric, high-clarity) |
| Code font | JetBrains Mono (SQL display) |
| Layout | 3-zone: fixed header / history sidebar / main query+results panel |
| Mic button | Gold pulse-ring animation + waveform bars |
| Language dropdown | Sarvam language codes with native name labels |
| Charts | Auto-detected type: bar (categorical), line (time-series), big-number (aggregate) |
| Animations | Staggered CSS keyframe reveal on load; result rows animate in |
| Responsive | Mobile: sidebar collapses to icon strip; full-width single column |

### Entity Scope

```
Customer (1) ──< Account (1) ──< Transaction
```

| Entity | Key Columns |
|--------|-------------|
| customers | id, name, email, phone, created_at |
| accounts | id, customer_id, account_number, account_type, balance, status, created_at |
| transactions | id, account_id, transaction_type (credit/debit), amount, description, created_at |

### Query Type Scope

| Category | Examples |
|----------|---------|
| Filtered lists | Last N transactions, amount > X |
| Aggregations | Total credits today, count of transactions this week |
| Customer lookups | Account balances for customer ID X |
| Account-scoped | Recent debits for account number Y |
| Cross-entity joins | Customers who transacted above Z this week |
| Date-range | Transactions between date A and date B |

---

## Out of Scope

| Item | Reason |
|------|--------|
| User authentication / login | Open internal tool — no auth system |
| Write operations (INSERT/UPDATE/DELETE) | Read-only system by design |
| Multi-tenant data isolation | Single-tenant deployment |
| Real-time streaming / websockets | Batch query model only |
| Loan, mortgage, or product entities | Outside defined domain |
| Mobile-native (iOS/Android) app | Web browser only |
| Streamlit or any low-code UI | Excluded by constraint |
| Auto-generated scaffolding | Excluded by constraint |
| Fraud detection / ML scoring | Out of domain |
| Scheduled / recurring queries | Manual query interaction only |
| PDF / Excel export | Not in initial delivery |
| Live STT streaming (word-by-word) | Single-shot audio blob transcription only |
| Sarvam translation (text-to-text) | STT and TTS only; no translation API |
| Voice conversation memory | Each voice query is stateless |

---

## Assumptions

1. Supabase project is provisioned and accessible before deployment.
2. Anthropic Claude API key is available with sufficient quota.
3. Sarvam AI API key is obtained from `dashboard.sarvam.ai` before deployment.
4. **HTTPS is available in production** — browsers block `getUserMedia` (mic) on plain HTTP.
5. Application is deployed in a trusted internal network or behind a corporate VPN.
6. All users accessing this assistant are authorized to view the banking data.
7. Database schema does not change post-deployment without a code update to `prompt_builder.py`.
8. Query response time SLA: ≤ 5 seconds (excluding voice transcription round-trip, ≤ 8s with voice).

---

## Constraints (from Problem Statement)

| Constraint | Status |
|-----------|--------|
| No Streamlit or low-code UI | ✅ Plain HTML/CSS/JS only |
| No copy-paste templates | ✅ Fully custom design |
| No auto-generated scaffolding | ✅ Hand-written, modular code |
| Frontend: plain HTML + JavaScript | ✅ |
| Backend: Python (FastAPI) | ✅ |
| Modular, validated, production-ready code | ✅ |
| Secure DB connectivity + read-only enforcement | ✅ |
| Visualization: Chart.js or open-source libs | ✅ Chart.js 4.x |
| Voice: Sarvam AI STT + TTS | ✅ `saarika:v2` + `bulbul:v1` |
| UI: Best-in-class premium dark dashboard | ✅ Custom luxury design system |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Text query accuracy | ≥ 95% correct data on valid queries |
| Voice transcription accuracy | Dependent on Sarvam model; tested on standard queries |
| SQL safety | 100% of mutating queries blocked |
| Response time (text) | p95 < 5 seconds |
| Response time (voice round-trip) | p95 < 8 seconds |
| Relational query correctness | All JOINs produce non-duplicated, correct results |
| Error handling | Zero unhandled exceptions surfaced to user |
| UI quality | Custom design — passes visual review without redesign |
| Code quality | Modular, linted, documented — passes review without restructuring |

---

## Stakeholders

| Role | Responsibility |
|------|---------------|
| Business Analyst | Query examples, acceptance testing |
| Backend Developer | FastAPI, Claude AI, Sarvam voice, DB layer |
| Frontend Developer | HTML/CSS/JS premium dashboard |
| DBA / Supabase Admin | Schema, RLS, backups |
| Security Reviewer | SQL validation, secrets management, HTTPS enforcement |
| Sarvam AI Integration | API key provisioning, language configuration |
