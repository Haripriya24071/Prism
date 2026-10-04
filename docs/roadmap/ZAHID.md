# Zahid — Backend Core & AI Swarm Orchestration

**Owns:** `backend/main.py`, `config.py`, `errors.py`, `models/`, `intake/`, `agents/swarm.py`, `evaluation/`, `output/heatmap.py`, `output/investor_score.py`, `output/pivot.py`, `middleware/log_sanitizer.py`.  
**Does not touch:** `backend/context/`, `backend/gcp/` (Haripriya), `backend/agents/personas.py` and `prompts.py` (Swapnil), `frontend/`.  
**Governing docs:** [ARCHITECTURE.md](../../ARCHITECTURE.md), [SCHEMA.md](../../SCHEMA.md), [RULES.md](../../RULES.md) (ARCH-001 to 010, 013, SEC-001 to 007)

---

## Current Status Overview
- **Phase 0 (Foundation & Contracts):** ✅ 100% Complete. FastAPI app, Pydantic v2 models, typed errors, config structure ready.
- **Phase 1 (Intake Processor):** ✅ 100% Complete. Conversational chat, JSON structured field extraction, Gemini Vision image analysis, document parsers.
- **Phase 2 (Swarm & Key Pool Rotation):** ✅ 100% Complete. High-availability Gemini AI Studio Key Pool (12-20 keys, ~180 RPM throughput, thread-safe round-robin, automatic 429/401 fallback). 6-Agent parallel execution verified live.
- **Phase 3 (Evaluation & Merge):** ✅ 90% Complete. Evaluator rubric, Pro/Flash model synthesis, mathematical heatmap, investor score calculation.
- **Phase 4 (Integration & Hardening):** 🟡 80% Complete. Backend running on port 8000. BigQuery tables connected. Pivot suggester operational.

---

## Phase 0 — Foundation and Contracts (Completed)

| # | Deliverable | Location | Status |
|---|-------------|----------|--------|
| 0.1 | FastAPI app, `uvicorn` setup, CORS from env, requirements specification | `backend/main.py`, `requirements.txt` | ✅ Done |
| 0.2 | `config.py`: Centralised settings, timeouts, model aliases, key pool loader | `backend/config.py` | ✅ Done |
| 0.3 | `errors.py`: Typed exceptions (`SwarmError`, `AgentTimeoutError`, `IntakeError`, `MergeError`) | `backend/errors.py` | ✅ Done |
| 0.4 | All Pydantic models matching SCHEMA.md (`ChatRequest`, `IntakePackage`, `ContextPackage`, `AgentOutput`, `ScoreMatrix`, `MergedBRD`, `LineageTag`, `HeatmapData`, `InvestorScore`) | `backend/models/` | ✅ Done |
| 0.5 | SSE event streaming generator for live client updates | `backend/sse_manager.py` | ✅ Done |
| 0.6 | Session ID UUID validation on all route handlers | `backend/models/intake.py` | ✅ Done |
| 0.7 | Logging configuration with key redaction | `backend/logging_config.py` | ✅ Done |

---

## Phase 1 — Intake Processing (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 1.1 | `POST /intake/session`, `GET /intake/session/{id}` | Session lifecycle management | ✅ Done |
| 1.2 | `intake/conversation.py`: Multi-turn Gemini Flash intake | Dynamic single-question turns until all 6 fields acquired | ✅ Done |
| 1.3 | `intake/extractor.py`: Structured JSON extraction | Validates region against ISO 3166-1 allowlist, extracts stage/budget | ✅ Done |
| 1.4 | `intake/vision.py`: Gemini Multimodal Vision analysis | Accepts JPEG/PNG diagrams/wireframes up to 10MB | ✅ Done |
| 1.5 | `POST /intake/upload`: MIME validation by magic bytes | PyPDF2 and python-docx text extraction | ✅ Done |

---

## Phase 2 — Swarm Orchestration & Multi-Key Pool (Completed & Verified)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 2.1 | **High-Throughput Gemini Key Pool (`backend/config.py`)** | Thread-safe `RotatingGeminiModel` rotating across 12-20 AI Studio keys. Automatically bypasses rate limits (429) and invalid keys by failing over to the next key. | ✅ Done |
| 2.2 | **Vertex AI Compatibility Shim (`backend/config.py`)** | Drop-in `GenerationConfig`, `Part`, and `Content` abstractions allowing code to run effortlessly on Google AI Studio keys without GCP billing blocks. | ✅ Done |
| 2.3 | **6-Agent Swarm Orchestration (`backend/agents/swarm.py`)** | Executes all 6 personas in parallel via `asyncio.gather()`. 45-second resilient timeout. Partial failure policy allows run to proceed if ≥ 4 agents succeed. | ✅ Done |
| 2.4 | Robust JSON stripping & parsing in `swarm.py` | Extracts valid JSON from model output regardless of markdown fences or commentary. | ✅ Done |
| 2.5 | `POST /generate` and `GET /generate/stream/{id}` | Dispatches live progress SSE events (`agent_status`, `context_ready`, `evaluation_complete`, `brd_ready`). | ✅ Done |

**Verification Gate:** Verified live in terminal — 6 agents ran in parallel, 5/5 active agents generated complete 6-section BRDs in 10–25s without crashing.

---

## Phase 3 — Evaluation and Merge Engine (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 3.1 | `evaluation/rubric.py`: Scoring criteria weights | Feasibility (25%), Market Timing (20%), Regulatory Safety (20%), User Adoption (20%), Competitive Moat (15%). | ✅ Done |
| 3.2 | `evaluation/evaluator.py`: Impartial scoring pass | Evaluates all agent outputs and generates confidence scores backed by data citations. | ✅ Done |
| 3.3 | `evaluation/merger.py`: Synthesis engine | Selects highest-composite base BRD and transplants winning sections from competing personas, preserving `LineageTag`. | ✅ Done |
| 3.4 | `output/heatmap.py`: Mathematical divergence calculation | Standard deviation across section scores mapped to 0–100 risk scale. Pure math, zero I/O. | ✅ Done |
| 3.5 | `output/investor_score.py`: Weighted readiness score | Calculates composite 0–100 score and identifies red-flag gaps. | ✅ Done |
| 3.6 | `GET /brd/{id}`: Full BRD retrieval | Returns merged document, lineage metadata, heatmap, and investor scorecard. | ✅ Done |

---

## Phase 4 — Pipeline Hardening & Demo Freeze (Active)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 4.1 | Pipeline integration in `backend/pipeline.py` | Coordinates Intake → Context → Swarm → Evaluation → Merge → Output. | ✅ Done |
| 4.2 | Pivot Suggester verification (`backend/output/pivot.py`) | Triggers 3 strategic pivots with projected scores if investor readiness < 60. | ✅ Done |
| 4.3 | Local verification test runs | Backend running on `http://localhost:8000` with active Swagger UI. | ✅ Done |
| 4.4 | Final demo freeze | Zero code changes during rehearsals; bug fixes only. | 🔄 Active |

**Exit Criteria:** 3 consecutive end-to-end runs succeed under 50s total execution time.
