# PRISM — System Architecture & Design Specification

---

## 1. System Overview

PRISM is an enterprise-grade multi-modal AI intelligence pipeline engineered with six modular processing layers. Each layer adheres strictly to a single responsibility principle, defined input/output contracts, and structured error boundaries.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER (React 18 + Vite — Vercel / Localhost)                                   │
│                                                                                        │
│  ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌───────────────────────┐  │
│  │  ChatBox         │ │  FileUpload    │ │  AgentGrid     │ │  BRDViewer +          │  │
│  │  (Text + Voice)  │ │  (Img + Doc)   │ │  (Live SSE)    │ │  ScoreCard + Heatmap  │  │
│  └────────┬─────────┘ └───────┬────────┘ └────────┬───────┘ └───────────────────────┘  │
│           │                   │                   │                                    │
└───────────┼───────────────────┼───────────────────┼────────────────────────────────────┘
            │   REST (HTTP)     │                   │  SSE Stream (`/generate/stream`)
┌───────────▼───────────────────▼───────────────────▼────────────────────────────────────┐
│  API & ORCHESTRATION LAYER (FastAPI — Railway / Localhost:8000)                        │
│                                                                                        │
│  POST /intake/session    POST /intake/chat    POST /intake/upload                      │
│  POST /generate          GET  /generate/stream/{id}                                    │
│  GET  /brd/{id}          GET  /brd/{id}/pdf?view={investor|technical|regulatory}       │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  HIGH-THROUGHPUT GEMINI KEY POOL & SHIM (12-20 AI Studio Keys — 180+ RPM Free)   │  │
│  │  Thread-Safe Round-Robin │ Instant 429/401 Failover │ Vertex AI Compatibility    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  INTAKE PROCESSOR                                                                │  │
│  │  Conversational Gemini Flash  │  Gemini Multimodal Vision  │  Doc Extraction     │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  CONTEXT HARVESTER  (asyncio.gather — 5 Parallel Sources)                        │  │
│  │  NewsAPI │ World Bank Open Data │ Crunchbase │ Govt Open Data │ Gemini Grounding │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  SWARM LAYER  (asyncio.gather — 6 Gemini Flash Personas in Parallel)             │  │
│  │  VC │ Lean Founder │ Enterprise CTO │ UX Researcher │ Regulator │ Adversarial    │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌───────────────────────────────┐      ┌───────────────────────────────────────────┐  │
│  │  EVALUATION RUBRIC ENGINE     │ ───► │  SYNTHESIS & MERGE ENGINE                 │  │
│  │  5 Criteria × 6 Sections      │      │  Winning Base BRD + Section Transplantation│ │
│  └───────────────────────────────┘      └───────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  OUTPUT ANALYSIS & REFRAMING                                                     │  │
│  │  Divergence Heatmap │ Investor Readiness Score │ Pivot Suggester │ ReportLab PDF │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────────────────────┐
│  GOOGLE CLOUD PERSISTENCE & ANALYTICS LAYER                                            │
│                                                                                        │
│  Google Cloud Storage (GCS)                    Google BigQuery (Sandbox & Prod)        │
│  - Bucket: `prism-outputs`                     - Dataset: `prism_data`                 │
│  - Session Path: `{session_id}/agent_*.json`   - Tables: `brd_runs`                    │
│  - Merged BRD: `{session_id}/merged_brd.json`  - Logs: `context_harvest_logs`          │
│  - PDF Artifacts: `{session_id}/output_*.pdf`  - Local/Dev: In-memory & Silent Stream  │
│  - Hybrid: Local GCS-schema fallback in dev                                            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Boundary Map

```
backend/
├── main.py                     (Thin FastAPI orchestrator — route handlers < 30 lines)
├── config.py                   (Central settings, 20-key pool, RotatingGeminiModel shim)
├── errors.py                   (Typed exception hierarchy: SwarmError, IntakeError, etc.)
├── sse_manager.py              (Server-Sent Events event stream broadcaster)
├── pipeline.py                 (End-to-end multi-stage pipeline coordinator)
├── session_store.py            (Thread-safe session state store)
├── intake/
│   ├── conversation.py         (Multi-turn Gemini chat turn handler)
│   ├── vision.py               (Gemini Multimodal image analysis for wireframes/diagrams)
│   ├── document.py             (PyPDF2 and python-docx text extraction)
│   └── extractor.py            (Structured JSON extraction: region, stage, budget)
├── context/
│   ├── harvester.py            (Parallel orchestrator across all 5 context sources)
│   ├── newsapi.py              (Industry news articles with local caching)
│   ├── worldbank.py            (Macroeconomic indicators: GDP, inflation, ease of business)
│   ├── crunchbase.py           (Competitor funding history with mock fallback)
│   ├── govtdata.py             (Statutory compliance and open data flags)
│   └── grounding.py            (Gemini Search Grounding for cultural context)
├── agents/
│   ├── swarm.py                (Parallel execution of 6 personas with 45s resilient timeout)
│   ├── personas.py             (Persona definitions and hard constraint axes)
│   └── prompts.py              (Enriched system prompts mandating 6-section JSON + citations)
├── evaluation/
│   ├── evaluator.py            (Scores all 6 BRDs against 5 weighted rubric criteria)
│   ├── rubric.py               (Rubric constants: Feasibility, Timing, Safety, Adoption, Moat)
│   └── merger.py               (Transplants highest-scoring sections into unified BRD)
├── output/
│   ├── heatmap.py              (Mathematical divergence standard deviation 0-100)
│   ├── investor_score.py       (Weighted composite readiness score + gap flags)
│   ├── pivot.py                (Generates 3 strategic pivots if score < 60)
│   ├── assumptions.py          (Identifies unstated assumptions with confidence ratings)
│   ├── failure_sim.py          (Adversarial failure simulation with mitigations)
│   ├── stakeholder.py          (Reframes BRD for Investor, Technical, and Regulatory views)
│   └── pdf_export.py           (ReportLab asynchronous PDF generator)
├── gcp/
│   ├── storage.py              (Hybrid Cloud Storage read/write with GCS-schema fallback)
│   └── bigquery.py             (Asynchronous fire-and-forget audit logger)
└── models/
    ├── intake.py               (Pydantic: ChatRequest, UploadRequest, IntakePackage)
    ├── context.py              (Pydantic: ContextPackage, NewsItem, MarketData)
    ├── agents.py               (Pydantic: AgentPersona, AgentOutput, ScoreMatrix)
    ├── brd.py                  (Pydantic: MergedBRD, BRDSection, LineageTag)
    └── output.py               (Pydantic: HeatmapData, InvestorScore, PivotSuggestion)
```

**Strict Architectural Invariant (No Upward Imports):**
`main.py → pipeline.py → agents/ intake/ context/ output/ → gcp/ → models/ → errors.py → config.py`

---

## 3. High-Throughput Gemini Key Pool Architecture

To eliminate rate limits (15 RPM free tier) and bypass cloud billing bottlenecks, PRISM uses a **Thread-Safe Rotating Key Pool** in `backend/config.py`:

```
                       ┌──────────────────────┐
                       │  Incoming LLM Call   │
                       └──────────┬───────────┘
                                  │
                       ┌──────────▼───────────┐
                       │ RotatingGeminiModel  │
                       └──────────┬───────────┘
                                  │ Atomic Round-Robin Index
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
│ Gemini Key #1     │   │ Gemini Key #2     │   │ Gemini Key #N     │
│ (15 RPM)          │   │ (15 RPM)          │   │ (15 RPM)          │
└─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
          ┌───────────────────────▼───────────────────────┐
          │ Success? ──► Return response                  │
          │ 429 / 401? ──► Log Warning & Rotate Next Key │
          └───────────────────────────────────────────────┘
```

- **Pool Capacity:** 12 to 20 keys = **180 to 300 Requests Per Minute (RPM)**.
- **Failover Strategy:** If any key encounters `429 (ResourceExhausted)` or `401 (InvalidToken)`, the client automatically falls over to the next key without failing the agent invocation.
- **Model Resolution:** Defaults to `gemini-flash-latest` (Gemini 2.0 Flash) for sub-second generation and multimodal intake.

---

## 4. End-to-End Execution Sequence

| Step | Component | Method / Operation | Latency (P95) | Artifact Output |
| :--- | :--- | :--- | :--- | :--- |
| **1. Intake** | `intake/conversation.py` | Multi-turn chat extraction | < 3s / turn | `IntakeExtraction` |
| **2. Multimodal** | `intake/vision.py` | Image / diagram analysis | < 4s | Extracted visual context |
| **3. Harvesting** | `context/harvester.py` | `asyncio.gather(5 sources)` | < 6s | `ContextPackage` |
| **4. Swarm** | `agents/swarm.py` | 6 Personas in parallel | < 20s | 6 × `agent_{name}.json` |
| **5. Evaluation** | `evaluation/evaluator.py`| Rubric scoring (5 criteria) | < 8s | `ScoreMatrix` |
| **6. Merge** | `evaluation/merger.py` | Section transplantation | < 8s | `MergedBRD` + `LineageTag` |
| **7. Analytics** | `output/heatmap.py` | Mathematical divergence | < 50ms | `HeatmapData` |
| **8. Readiness** | `output/investor_score.py`| Weighted composite (0-100) | < 50ms | `InvestorScore` |
| **9. Pivot** | `output/pivot.py` | Strategic pivots (if < 60) | < 4s | 3 Pivot Directions |
| **10. Post-Analysis**| `output/assumptions.py` | Assumptions & Failure sim | < 6s | Enriched BRD sections |
| **11. Export** | `output/pdf_export.py` | ReportLab PDF compilation | < 2s | 3 Stakeholder PDFs |
| **12. Persistence**| `gcp/storage.py` & `bq.py`| Hybrid GCS & BigQuery log | Background | GCS blobs + BQ rows |

---

## 5. SSE Event Protocol

The frontend connects to `GET /generate/stream/{session_id}`. Events are streamed in real time:

```
event: agent_status
data: {"agent": "vc", "status": "running", "progress_pct": 20}

event: context_ready
data: {"sources": ["newsapi", "worldbank", "crunchbase", "grounding"], "progress_pct": 35}

event: agent_status
data: {"agent": "vc", "status": "complete", "progress_pct": 50}

event: evaluation_complete
data: {"winning_agent": "cto", "score": 84, "progress_pct": 80}

event: brd_ready
data: {"session_id": "...", "investor_readiness_score": 84, "progress_pct": 100}
```

---

## 6. Enterprise Scale & Vertex AI Path

For enterprise deployment, PRISM transitions seamlessly to **Vertex AI Application Default Credentials (ADC)** and dedicated BigQuery analytics by toggling `ENV=production` in `config.py`. All interfaces, schemas, and data structures remain 100% identical.
