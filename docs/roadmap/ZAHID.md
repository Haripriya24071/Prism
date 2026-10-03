# Zahid — Backend Core

**Owns:** `backend/main.py`, `config.py`, `errors.py`, `models/`, `intake/`, `agents/swarm.py`, `evaluation/`, `output/heatmap.py`, `output/investor_score.py`, `output/pivot.py`, `middleware/log_sanitizer.py`
**Does not touch:** `context/`, `gcp/` (Haripriya), `agents/personas.py` and `prompts.py` (Swapnil), `frontend/`.
**Governing docs:** [ARCHITECTURE.md](../../ARCHITECTURE.md), [SCHEMA.md](../../SCHEMA.md), [RULES.md](../../RULES.md) (ARCH-001 to 010, 013, SEC-001 to 007)

Phases are gated by exit criteria, not dates. Phase 0 blocks everyone else.

---

## Phase 0 — Foundation and Contracts (critical path)

| # | Deliverable | Location |
|---|-------------|----------|
| 0.1 | FastAPI app, `uvicorn` run, CORS from env, `python-magic` in requirements | `main.py`, `requirements.txt` |
| 0.2 | `config.py`: all model names, bucket, table names, timeouts, key pool from env. No string literals elsewhere (ARCH-009) | `config.py` |
| 0.3 | `errors.py`: typed exceptions (key exhausted, agent failed, harvest failed, validation) | `errors.py` |
| 0.4 | **All Pydantic models**, matching SCHEMA.md: `ChatRequest`, `IntakePackage`, `ContextPackage`, `AgentOutput`, `ScoreMatrix`, `MergedBRD`, `LineageTag`, `HeatmapData`, `InvestorReadiness` | `models/` |
| 0.5 | SSE event models for every event in ARCHITECTURE.md | `models/output.py` |
| 0.6 | Session ID UUIDv4 validator reused on every route (SEC-002) | `models/intake.py` |
| 0.7 | `LogSanitizer` middleware that redacts keys (SEC-006) | `middleware/` |
| 0.8 | Publish the models and event spec. Swapnil and Haripriya review and sign off | review gate |

**Exit:** `python -c "import backend.main"` and `mypy .` pass. Models reviewed by Swapnil and Haripriya. Import direction follows ARCH-001.

---

## Phase 1 — Intake

| # | Deliverable | Notes |
|---|-------------|-------|
| 1.1 | `POST /intake/session`, `GET /intake/session/{id}` | handlers max 30 lines, one service call (ARCH-008) |
| 1.2 | `intake/conversation.py`: Gemini Flash chat turns, asks only what's missing | |
| 1.3 | `intake/extractor.py`: pulls region, industry, stage, budget, constraints. Region validated against ISO 3166-1 allowlist, industry sanitised (SEC-003, SEC-004) | LLM output is untrusted |
| 1.4 | `intake/vision.py` and `intake/document.py` (PyPDF2, python-docx) | |
| 1.5 | `POST /intake/upload` with magic-byte MIME check and size limit (SEC-005) | |
| 1.6 | Signal to Haripriya's harvester once region is detected | via a function call defined in the Phase 0 contract |

**Exit:** a messy idea in chat produces a valid `ExtractedIntake` and `IntakePackage`. Bad MIME types are rejected. Tests from Ritika pass.

---

## Phase 2 — Swarm and Key Rotation

| # | Deliverable | Notes |
|---|-------------|-------|
| 2.1 | Key pool in `config.py`: round-robin, skip empty slots, on 429 retry with the next key, raise `KeyExhausted` after one full cycle | the doc's `get_next_key` is not concurrency-safe and ignores empty keys. Fix both |
| 2.2 | Gemini client wrapper: async, timeout from config, JSON-mode output, validation into `AgentOutput` | no `requests`, no blocking calls (ARCH-010) |
| 2.3 | `agents/swarm.py`: `asyncio.gather` over six agents, each writes its result to storage immediately on completion (DB-003) | uses Haripriya's `gcp/storage.py` |
| 2.4 | Partial failure policy: one agent failing must not kill the run. Proceed if at least 4 of 6 succeed, mark the rest failed | the merge and heatmap must cope with fewer than 6 |
| 2.5 | Wire Swapnil's `personas.py` and `prompts.py` | |
| 2.6 | `POST /generate` and `GET /generate/stream/{id}` with all SSE events | |

**Exit:** six agent outputs land in storage for a test session. SSE emits the full event sequence. Swarm P95 under 20s on the free tier.

---

## Phase 3 — Evaluation and Merge

| # | Deliverable | Notes |
|---|-------------|-------|
| 3.1 | `evaluation/rubric.py`: weights from PRD 4.4 as constants | 25 / 20 / 20 / 20 / 15 |
| 3.2 | `evaluation/evaluator.py`: one Pro call, five sections by five criteria, every score with a data citation. Reject uncited scores | |
| 3.3 | `evaluation/merger.py`: highest composite is the base, transplant any section scoring higher, attach `LineageTag` | |
| 3.4 | `output/heatmap.py`: std dev per section normalised to 0–100, pure math, no I/O | |
| 3.5 | `output/investor_score.py`: weighted sum, gap flags, pure math, no I/O | |
| 3.6 | Pro-model rate limit handling: two calls per run on a 2 RPM tier. Queue or wait rather than fail | |
| 3.7 | `GET /brd/{id}` returns the full merged BRD with heatmap and score | |

**Exit:** a full run yields `merged_brd.json`, `heatmap.json`, `investor_readiness.json`. Calculation modules have unit tests with fixed inputs. End to end under 50s P95.

---

## Phase 4 — Integration and Hardening

| # | Deliverable | Notes |
|---|-------------|-------|
| 4.1 | Hook Haripriya's assumptions, failure sim, BigQuery logging and PDF into the pipeline | calls only, her code |
| 4.2 | Five concurrent sessions test | PRD success metric |
| 4.3 | Pivot Suggester (`output/pivot.py`), fires if score < 60 | **stretch.** Only if Phases 0–3 are green |
| 4.4 | Deploy to Railway, set env, verify SSE survives the proxy | |
| 4.5 | Vertex AI job tracking | **stretch.** In-process session state is the primary mechanism (DB-008) |

**Exit:** full run on the deployed backend from the deployed frontend.

---

## Phase 5 — Freeze

- No new features after freeze
- `mypy`, `pytest`, `import main` clean
- Confirm no keys in logs
- Verify the model names still resolve on your keys. ARCHITECTURE and TECHSTACK name Gemini 1.5, which may be retired. Check this in Phase 0, not here

**Exit:** demo run succeeds three times in a row.

---

## Dependencies

| Need | From | By |
|------|------|----|
| `personas.py`, `prompts.py` | Swapnil | start of Phase 2 |
| `gcp/storage.py` | Haripriya | start of Phase 2 |
| `context/harvester.py` | Haripriya | end of Phase 2 |
| Test fixtures and pytest suite | Ritika | continuous |

## Risks

- **Phase 0 is the team's bottleneck.** Ship models first, even before the app runs.
- **Free-tier limits.** Gemini Pro at 2 RPM is the tightest constraint. Test it with concurrent sessions early.
- **Model deprecation.** Verify model IDs before building on them.
