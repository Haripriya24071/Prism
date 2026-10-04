# PRISM — System Engineering & Architectural Rules

> These rules are strictly enforced across the codebase. If a rule conflicts with a feature request, the rule wins.

---

## 1. Architectural Rules (ARCH)

- **ARCH-001: Module boundary is absolute.**
  Each backend module owns exactly one domain. No module reaches across its boundary.
  *Dependency Flow:* `main.py → pipeline.py → agents/ intake/ context/ output/ → gcp/ → models/ → errors.py → config.py`

- **ARCH-002: `main.py` is a thin orchestrator only.**
  Maximum 150 lines. Route handlers maximum 30 lines. All business logic resides in service modules.

- **ARCH-003: No circular imports.**
  Verify with `python -c "import backend.main"` before every commit.

- **ARCH-004: All public symbols in `__all__`.**
  Internal and private helpers must be prefixed with `_`.

- **ARCH-005: React components use default exports; all other JS uses named exports.**

- **ARCH-006: No barrel index files in frontend.**
  Import by explicit path (e.g. `import ScoreCard from '@/components/ScoreCard/ScoreCard'`). No `src/components/index.js`.

- **ARCH-007: File length thresholds.**
  - Python service module: Max 350 lines
  - React component: Max 250 lines
  - Orchestrators (`main.py`, `pipeline.py`): Max 150 lines
  - Test suites: Max 400 lines

- **ARCH-008: No synchronous blocking in async functions.**
  Use `httpx.AsyncClient` for network I/O, `asyncio.sleep()` for delays, and `asyncio.to_thread()` for CPU-heavy tasks (e.g. ReportLab PDF compilation, image decoding). Never `time.sleep()` or blocking filesystem calls in `async def`.

- **ARCH-009: No hardcoded configuration strings.**
  All model names, timeouts, bucket identifiers, and table names must originate from `config.py` via environment variables.

- **ARCH-010: SSE connections must clean up on unmount.**
  Frontend `EventSource` instances must close in component unmount cleanup functions (`useSSE.js`).

---

## 2. AI & Model Execution Rules (AI)

- **AI-001: Thread-Safe Key Pool Routing.**
  Never invoke `genai.configure()` or instantiate raw Gemini clients inside service modules. All LLM calls must route through `get_flash_model()` or `get_pro_model()` in `backend/config.py` to ensure thread-safe round-robin key rotation and immediate failover on HTTP 429/401 errors.

- **AI-002: Prompt Citation Integrity.**
  System prompts must explicitly enforce the `[SOURCE: source_name]` tag on every empirical claim, competitor reference, or regulatory guideline. Uncited factual claims are rejected during evaluation.

- **AI-003: Partial Swarm Failure Policy.**
  The swarm must proceed if at least 4 of 6 agents succeed. Failed agents are marked with `failed=True` and skipped during the merge transplantation step.

---

## 3. Security & Validation Rules (SEC)

- **SEC-001: Session UUID Validation.**
  All endpoints accepting a `session_id` must validate it as a valid UUID v4 format via regex pattern `^[a-zA-Z0-9_-]+$`.

- **SEC-002: File Upload Magic-Byte Verification.**
  Never trust client-supplied MIME types. Validate file headers using magic bytes (`\xff\xd8\xff` for JPEG, `\x89PNG` for PNG, `%PDF` for PDF).

- **SEC-003: Strict Key Redaction in Logs.**
  API keys, service account credentials, and user private data must never be logged. Structured logging must sanitize all output strings.

- **SEC-004: File Size Hard Cap.**
  All file uploads are capped at 10 MB. Files exceeding this limit are rejected immediately with an HTTP 413 payload before processing.

---

## 4. Cloud & Persistence Rules (DB)

- **DB-001: GCS Path Structure Parity.**
  Local fallback storage must mirror the exact production GCS folder hierarchy: `{session_id}/{filename}` under `/tmp/prism-sessions/`.

- **DB-002: Asynchronous Audit Logging.**
  BigQuery logging (`log_run_to_bigquery`, `log_context_harvest`) must be executed as background tasks via `asyncio.create_task()`. Database logging must never block the client response path.

- **DB-003: Content-Type Enforced.**
  All JSON documents written to GCS or fallback storage must specify `content_type="application/json"`.

---

## 5. Frontend & UI Rules (UI)

- **UI-001: Zero Hardcoded Colors.**
  All markup must reference CSS custom properties defined in `src/index.css` (e.g. `var(--color-surface)`). Raw hex values in components are forbidden.

- **UI-002: Motion Property Whitelist.**
  Animations must only animate `transform` and `opacity`. Never animate layout-triggering properties (`width`, `height`, `margin`, `top`).

- **UI-003: Respect Reduced Motion.**
  All animations must include a `@media (prefers-reduced-motion: reduce)` override that collapses movement into instant opacity transitions.

- **UI-004: Loading State Feedback.**
  Every high-latency transition must display visual feedback (e.g. `HandshakeLoader` during swarm deliberation) informing the user which pipeline layer is active.
