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
│  {session_id}/output_*.pdf             prism_data.evaluator_scores    │
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
| 10 | Pivot Check | If score < 60 → Pivot Suggester fires 3 pivot directions with projected scores (built — not roadmap). | Appended to `investor_readiness.json` |
| 11 | Assumption Flags | BRD scanned for hidden assumptions. Each surfaced with evidence rating and action item. | Appended to `merged_brd.json` |
| 12 | Failure Sim | Agent 6's adversarial output processed into top 3 failure modes with probability + mitigation. | Appended to `merged_brd.json` |
| 13 | PDF Export | ReportLab generates 3 PDFs (Investor / Technical / Regulatory views). | `output_investor.pdf, output_technical.pdf, output_regulatory.pdf` in GCS |
| 14 | Client | SSE stream delivers agent statuses live. Final render: heatmap → BRD viewer → scorecard. | Full UI experience |

---

## Concurrency Model

```python
# Vertex AI init — once at startup
vertexai.init(project=settings.GCP_PROJECT_ID, location="us-central1")

# Context Harvester — 5 APIs in parallel (one is Gemini Grounding via Vertex)
context_results = await asyncio.gather(
    fetch_news(region, industry),
    fetch_worldbank(region),
    fetch_crunchbase(industry),
    fetch_govtdata(region, industry),
    fetch_gemini_grounding(region, industry),   # Vertex AI call
    return_exceptions=True
)

# Swarm — 6 Flash agents in parallel via Vertex AI
flash = GenerativeModel("gemini-2.0-flash")
agent_results = await asyncio.gather(
    run_agent("vc",          intake_package, flash),
    run_agent("lean",        intake_package, flash),
    run_agent("cto",         intake_package, flash),
    run_agent("ux",          intake_package, flash),
    run_agent("regulator",   intake_package, flash),
    run_agent("adversarial", intake_package, flash),
)

# Post-merge analysis — 3 Flash calls in parallel
post_merge = await asyncio.gather(
    flag_assumptions(merged_brd, context, flash),
    extract_failure_modes(adversarial_output, flash),
    reframe_stakeholder_views(merged_brd, flash),
)

# GCS reads for merge — parallel
outputs = await asyncio.gather(
    *[read_agent_output(session_id, name) for name in AGENT_NAMES]
)

# BigQuery logging — fire and forget
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
| Post-merge analysis (assumptions + failure sim + stakeholder) | < 15 seconds (3 Flash parallel) |
| PDF generation | < 3 seconds |
| **Total end-to-end** | **< 65 seconds P95** |

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

## Authentication & Quota

PRISM calls Gemini through the Vertex AI SDK (`google-cloud-aiplatform`).
Authentication uses a single GCP service account with Application Default Credentials (ADC).
Quota is managed at the GCP project level — no per-key rotation required or used.

```python
# config.py — single ADC auth, no key pool
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_REGION)

def get_flash_model() -> GenerativeModel:
    return GenerativeModel("gemini-2.0-flash")

def get_pro_model() -> GenerativeModel:
    return GenerativeModel("gemini-1.5-pro")
```

Total Gemini calls per BRD run:
- 1× Flash (intake/conversation extractor)
- 5× Flash (context grounding — 1 of the 5 context sources)
- 6× Flash (swarm — all agents in parallel)
- 1× Flash (assumption flagging — post merge)
- 1× Flash (failure mode extraction — post merge)
- 1× Flash (stakeholder view reframing — post merge)
- 1× Pro  (evaluator — scores all 6 BRDs)
- 1× Pro  (merge engine)
Total: 16 calls per run. All Flash calls fit within Vertex AI Flash quota. Pro calls: 2 per run.
