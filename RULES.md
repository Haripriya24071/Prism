# PRISM — Rules

> These rules are enforced on every file. If a rule conflicts with a feature request, the rule wins.

---

## Architecture Rules

**ARCH-001: Module ownership is absolute.**
Each backend module owns one domain. No module reaches across its boundary.
Dependency direction: `main.py → agents/ intake/ context/ output/ → gcp/ → models/ → errors.py → config.py`

**ARCH-002: `main.py` is a thin orchestrator only.**
Max 150 lines. Route handlers max 30 lines. All logic in service modules.

**ARCH-003: No circular imports.**
Verify with `python -c "import backend.main"` before every commit.

**ARCH-004: All public symbols in `__all__`.**
Private helpers prefixed with `_`.

**ARCH-005: React components use default exports. All other JS uses named exports.**

**ARCH-006: No barrel index files.**
Import by explicit path. No `src/components/index.js`.

**ARCH-007: File size limits.**
| Type | Limit |
|------|-------|
| Python service module | 350 lines |
| React component | 250 lines |
| `main.py` | 150 lines |
| Test files | 400 lines |

**ARCH-008: No logic in route handlers.**
Validate input → call one service function → return response. Nothing else.

**ARCH-009: No string-typed config in code.**
All model names, bucket names, table names, timeouts from `config.py` via env vars.

**ARCH-010: No synchronous blocking in async functions.**
Use `httpx.AsyncClient` for HTTP. `asyncio.sleep()` for delays. `asyncio.to_thread()` for CPU-bound work. Never `requests`, `time.sleep()`, or `open()` on large files inside `async def`.

**ARCH-011: Canvas animations use `requestAnimationFrame` exclusively.**
```javascript
useEffect(() => {
  let animFrameId;
  let isRunning = true;
  function draw() {
    if (!isRunning) return;
    animFrameId = requestAnimationFrame(draw);
  }
  animFrameId = requestAnimationFrame(draw);
  return () => { isRunning = false; cancelAnimationFrame(animFrameId); };
}, []);
```

**ARCH-012: SSE connections cleaned up on unmount.**
```javascript
useEffect(() => {
  const source = new EventSource(`${API_BASE}/generate/stream/${sessionId}`);
  return () => source.close(); // REQUIRED
}, [sessionId]);
```

**ARCH-013: Pydantic models on every API endpoint.**
No raw `dict` in route signatures. No `Response(content=json.dumps(...))`.

---

## Security Rules

**SEC-001: All HTTP request bodies have a Pydantic v2 schema.**

**SEC-002: Session ID validated as UUID v4 on every endpoint before any lookup.**

**SEC-003: Region codes extracted from Gemini validated against ISO 3166-1 alpha-2 allowlist before use in API calls.**
LLM output is untrusted. Always sanitise.

**SEC-004: Industry strings from Gemini sanitised before use in API calls.**
```python
sanitised = re.sub(r'[^a-zA-Z0-9 \-]', '', industry).strip()[:100]
```

**SEC-005: File uploads validated by MIME type via magic bytes, not extension.**
Use `python-magic`. Allowed: `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `text/plain`.

**SEC-006: No API keys in any log entry.**
All logs pass through `LogSanitizer` middleware. Keys replaced with `[REDACTED]`.

**SEC-007: No user content in GCS paths.**
All paths derived from server-generated `session_id` only.

---

## Database Rules

**DB-001: All GCS blob paths derived from session_id only.**
Never use user-provided filenames or content in GCS paths.

**DB-002: All GCS writes confirmed before session status advances.**
Check `blob.exists()` or catch exception. A failed write that appears successful is worse than a visible failure.

**DB-003: Agent output blobs written immediately after each agent completes.**
Do not batch. Write on completion. Partial results preserved if swarm fails mid-run.

**DB-004: GCS reads check blob existence before download.**
Never call `download_as_text()` without first checking `blob.exists()`.

**DB-005: All GCS blobs written with `content_type="application/json"`.**

**DB-006: All BigQuery inserts use `insert_rows_json()` with Pydantic-validated dicts.**
Never string-interpolated SQL. Never raw user data in queries.

**DB-007: BigQuery writes are fire-and-forget.**
Wrap in `asyncio.create_task()`. Errors logged at WARNING. Never block the main pipeline.

**DB-008: Never query BigQuery from a hot path.**
BigQuery is for analytics and logging only. Session state during active runs lives in-process.

**DB-009: BigQuery table names always from `config.py`.**

**DB-010: All agent GCS reads in parallel.**
Use `asyncio.gather()`. Never a serial loop.

**DB-011: All context harvester API calls in parallel.**
`asyncio.gather(..., return_exceptions=True)`. One slow API never blocks.

**DB-015: Session IDs in GCS paths always lowercase.**
```python
blob_name = f"{session_id.lower()}/agent_{agent_name}.json"
```

---

## UI Rules

**UI-001: All colours use CSS custom property tokens.**
No hardcoded hex, RGB, or named colours in component styles.

**UI-002: All font sizes use CSS custom property scale tokens.**

**UI-003: Typography uses only the three defined font stacks.**
`--font-display`, `--font-body`, `--font-mono`. No other fonts.

**UI-004: All interactive elements keyboard-reachable with visible focus states.**
`:focus-visible` outline: 2px solid `--color-accent-signal`, offset 2px.

**UI-005: Canvas elements have text alternatives.**
Decorative canvas: `aria-hidden="true"`. Status canvas: `role="img"` + `aria-label`.

**UI-006: Colour contrast ratios meet WCAG 2.1 AA.**
Use only the pre-verified token pairs in `DESIGN.md`.

**UI-007: Agent status communicated by colour AND text label — never colour alone.**
Pending: grey + "Waiting". Running: blue pulse + "Thinking...". Complete: green + "Done". Failed: red + "Failed".

**UI-008: All form inputs have associated visible labels.**
Use `sr-only` class for visually hidden labels.

**UI-009: Dynamic content updates use ARIA live regions.**
Agent status changes, heatmap population, BRD section renders must use `aria-live="polite"`.

**UI-010: No layout shift after initial render.**
Skeleton states at exact same dimensions as loaded state.

**UI-011: Three breakpoints only.**
`768px` (tablet) and `1024px` (desktop). No others.

**UI-012: AgentGrid uses CSS Grid, not Flexbox.**
3 columns desktop, 2 tablet, 1 mobile.

**UI-013: `prefers-reduced-motion` respected.**
All animations disabled or reduced to opacity fade when user requests it.

**UI-014: Only `transform` and `opacity` animated.**
Never `width`, `height`, `top`, `left`, `margin`, `padding`. These trigger layout recalculation.

**UI-015: Canvas sized via `devicePixelRatio`.**
Called on mount and on every resize event (debounced 100ms).

**UI-016: Particle background canvas never blocks scroll or pointer events.**
```css
.particle-canvas { pointer-events: none; z-index: -1; }
```

**UI-017: No inline styles except for dynamic canvas/animation values.**

**UI-018: Heatmap risk level colour applied via `data-risk` attribute, not inline style.**

**UI-019: Agent accent colours applied via `data-agent` attribute on agent cards.**

---

## General

- All environment variables documented in `.env.example`. No undocumented vars.
- No `console.log` in production code. Use structured logging on the backend.
- Every PR must pass: `mypy` (backend), `eslint` (frontend), `pytest` (backend tests).
- Commit messages: `type(scope): description` — e.g. `feat(swarm): add key rotation logic`
