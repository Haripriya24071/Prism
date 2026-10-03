# PRISM — Architecture

---

## System Overview

PRISM is a multi-modal AI pipeline with six distinct processing layers. Each layer has a single responsibility, a defined input contract, and a defined output contract. No layer reaches across its boundary.

```
┌─────────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER (Vercel — React + Vite)                               │
│                                                                     │
│  ┌──────────────┐ ┌────────────┐ ┌───────────┐ ┌────────────────┐  │
│  │  ChatBox     │ │FileUpload  │ │ AgentGrid │ │ BRDViewer +    │  │
│  │ (Text+Voice) │ │(Img + Doc) │ │(Live SSE) │ │ ScoreCard +    │  │
│  └──────┬───────┘ └─────┬──────┘ └─────┬─────┘ │ Heatmap        │  │
│         │               │              │        └────────────────┘  │
└─────────┼───────────────┼──────────────┼─────────────────────────────┘
          │   REST / SSE  │              │  SSE stream
┌─────────▼───────────────▼──────────────▼─────────────────────────────┐
│  API LAYER (FastAPI on Railway)                                       │
│                                                                       │
│  POST /intake/session    POST /intake/chat    POST /intake/upload     │
│  GET  /session/{id}      GET  /generate/stream/{id}                   │
│  GET  /brd/{id}          GET  /brd/{id}/pdf                           │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  ORCHESTRATION (Vertex AI — tracks session state)             │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  INTAKE PROCESSOR                                              │   │
│  │  Conversational Gemini Flash  │  Gemini Vision  │  Doc Parser │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                           ↓                                           │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  CONTEXT HARVESTER  (asyncio.gather — all 5 in parallel)      │   │
│  │  NewsAPI │ World Bank │ Crunchbase │ Govt Data │ Gemini Ground │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                           ↓                                           │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  SWARM LAYER  (asyncio.gather — 6 Flash calls in parallel)    │   │
│  │  VC │ Lean Founder │ CTO │ UX Researcher │ Regulator │ Adversarial│
│  └────────────────────────────────────────────────────────────────┘   │
│                           ↓                                           │
│  ┌──────────────────────┐  ┌─────────────────────────────────────┐   │
│  │  EVALUATOR           │→ │  MERGE ENGINE                       │   │
│  │  Gemini 1.5 Pro      │  │  Gemini 1.5 Pro                     │   │
│  │  Scores all 6 BRDs   │  │  Best base + best sections          │   │
│  └──────────────────────┘  └─────────────────────────────────────┘   │
│                           ↓                                           │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │  OUTPUT LAYER                                                  │   │
│  │  Heatmap Calc │ Investor Score │ Pivot Suggester │ PDF Export  │   │
│  └────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────┐
│  GCP PERSISTENCE LAYER                                                │
│  Cloud Storage (GCS)                   BigQuery                       │
│  {session_id}/agent_*.json             prism_data.brd_runs            │
│  {session_id}/merged_brd.json          prism_data.context_harvest_logs│
│  {session_id}/output.pdf               prism_data.evaluator_scores    │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Module Boundary Map

```
main.py  (thin orchestrator only — max 150 lines)
  └── intake/
  │     ├── conversation.py   (Gemini Flash chat turns)
  │     ├── vision.py         (Gemini Vision for images)
  │     ├── document.py       (PyPDF2 + python-docx extraction)
  │     └── extractor.py      (pulls region, industry, stage from conversation)
  └── context/
  │     ├── harvester.py      (orchestrates all 5 API calls)
  │     ├── newsapi.py
  │     ├── worldbank.py
  │     ├── crunchbase.py
  │     ├── govtdata.py
  │     └── grounding.py      (Gemini Search Grounding)
  └── agents/
  │     ├── swarm.py          (asyncio.gather — fires all 6)
  │     ├── prompts.py        (all system prompts — data file, no logic)
  │     └── personas.py       (persona definitions and constraint axes)
  └── evaluation/
  │     ├── evaluator.py      (Gemini Pro scoring call)
  │     ├── rubric.py         (weighted criteria constants)
  │     └── merger.py         (Gemini Pro merge call)
  └── output/
  │     ├── heatmap.py        (std dev calculation — pure math, no I/O)
  │     ├── investor_score.py (weighted sum — pure math, no I/O)
  │     ├── pivot.py          (pivot suggester — fires if score < 60)
  │     ├── assumptions.py    (assumption flagging layer)
  │     ├── failure_sim.py    (failure mode simulation from Agent 6)
  │     ├── pdf_export.py     (ReportLab)
  │     └── stakeholder.py    (3 export views: investor / tech / regulatory)
  └── gcp/
  │     ├── storage.py        (GCS read/write)
  │     └── bigquery.py       (BQ insert — fire and forget)
  └── models/
  │     ├── intake.py         (Pydantic: ChatRequest, UploadRequest, IntakePackage)
  │     ├── context.py        (Pydantic: ContextPackage, NewsItem, MarketData)
  │     ├── agents.py         (Pydantic: AgentOutput, ScoreMatrix)
  │     ├── brd.py            (Pydantic: MergedBRD, BRDSection, LineageTag)
  │     └── output.py         (Pydantic: HeatmapData, InvestorScore, PivotSuggestion)
  └── errors.py               (custom exception classes)
  └── config.py               (all env vars, API key pool, model names)
```

**Dependency direction (strict — no upward imports):**
```
main.py → agents/ intake/ context/ output/ → gcp/ → models/ → errors.py → config.py
```

---

## End-to-End Data Flow

| Step | Layer | Action | Output |
|------|-------|--------|--------|
| 1 | Client | User speaks or types idea. Optional file upload. | Raw text / audio / file → FastAPI |
| 2 | Intake | Conversational Gemini Flash extracts region, industry, stage, constraints. Vision runs on images. Doc parser runs on files. | `intake_package.json` |
| 3 | Context | Harvester fires 5 API calls in parallel. Gemini Grounding for cultural layer. | `context_package` JSON — logged to BigQuery |
| 4 | Merge | Intake + file context + context package → unified `IntakePackage` | `intake_package.json` → GCS |
| 5 | Swarm | 6 Gemini Flash calls via `asyncio.gather()`. Each agent gets same input, different system prompt. Each output written to GCS immediately on completion. | 6 × `agent_{name}.json` in GCS |
| 6 | Evaluation | Gemini Pro receives all 6 BRDs + context. Scores each across 5 sections × 5 criteria. Every score backed by data citation. | `score_matrix.json` |
| 7 | Merge | Gemini Pro selects winning base BRD. Transplants highest-scoring section from each competing agent. | `merged_brd.json` with full lineage |
| 8 | Heatmap | Pure Python std dev across per-section scores → normalised 0–100 risk scale. | `heatmap.json` |
| 9 | Investor Score | Weighted sum of rubric scores → 0–100. Gap flags extracted. | `investor_readiness.json` |
| 10 | Pivot Check | If score < 60 → Pivot Suggester fires 3 pivot directions with projected scores. | Appended to `investor_readiness.json` |
| 11 | Assumption Flags | BRD scanned for hidden assumptions. Each surfaced with evidence rating and action item. | Appended to `merged_brd.json` |
| 12 | Failure Sim | Agent 6's adversarial output processed into top 3 failure modes with probability + mitigation. | Appended to `merged_brd.json` |
| 13 | PDF Export | ReportLab generates 3 PDFs (Investor / Technical / Regulatory views). | `output_{view}.pdf` in GCS |
| 14 | Client | SSE stream delivers agent statuses live. Final render: heatmap → BRD viewer → scorecard. | Full UI experience |

---

## Concurrency Model

```python
# Context Harvester — 5 APIs in parallel
context_results = await asyncio.gather(
    fetch_news(region, industry),
    fetch_worldbank(region),
    fetch_crunchbase(industry),
    fetch_govtdata(region, industry),
    fetch_gemini_grounding(region, industry),
    return_exceptions=True  # one slow API never blocks the others
)

# Swarm — 6 agents in parallel
agent_results = await asyncio.gather(
    run_agent("vc", intake_package),
    run_agent("lean", intake_package),
    run_agent("cto", intake_package),
    run_agent("ux", intake_package),
    run_agent("regulator", intake_package),
    run_agent("adversarial", intake_package),
)

# GCS reads for merge — parallel, not serial
outputs = await asyncio.gather(
    *[read_agent_output(session_id, name) for name in AGENT_NAMES]
)

# BigQuery logging — never blocks main pipeline
asyncio.create_task(_log_harvest_to_bq(context, session_id))
```

---

## Latency Targets

| Step | Target (P95) |
|------|-------------|
| Intake (conversational + extraction) | < 5 seconds |
| Context Harvester (5 APIs parallel) | < 8 seconds |
| Swarm (6 Flash calls parallel) | < 20 seconds |
| Evaluator (1 Pro call) | < 10 seconds |
| Merge Engine (1 Pro call) | < 10 seconds |
| Output calculations (heatmap + score) | < 200ms |
| PDF generation | < 3 seconds |
| **Total end-to-end** | **< 50 seconds P95** |

---

## SSE Stream Events

The frontend connects to `GET /generate/stream/{session_id}` immediately after generation starts. Events emitted:

```
event: agent_status
data: {"agent": "vc", "status": "running", "progress_pct": 20}

event: agent_status
data: {"agent": "vc", "status": "complete", "progress_pct": 35}

event: context_ready
data: {"sources": ["newsapi", "worldbank", "crunchbase"], "progress_pct": 15}

event: evaluation_complete
data: {"winning_agent": "lean", "score": 81, "progress_pct": 75}

event: brd_ready
data: {"session_id": "...", "investor_readiness_score": 74, "progress_pct": 100}
```

---

## API Key Rotation

```python
# config.py
GEMINI_KEY_POOL = [
    os.getenv(f"GEMINI_KEY_{i}") for i in range(1, 21)
]

def get_next_key() -> str:
    """Round-robin across 20 API keys."""
    idx = _key_counter % len(GEMINI_KEY_POOL)
    _key_counter += 1
    return GEMINI_KEY_POOL[idx]
```

Each swarm run consumes: 6 Flash calls + 2 Pro calls = 8 total API calls, distributed across the key pool.
