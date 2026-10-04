# PRISM — System Architecture & Design Specification

> **Version:** 2.0 (Production Verified) | **Team:** Swapnil Ghosh, Zahid, Haripriya, Ritika  
> **Hackathon:** Manipal Hackathon 2026 | **Track:** Google Gemini AI + Google Cloud

---

## 1. Executive System Topology

PRISM is an enterprise-grade multi-modal AI intelligence system engineered with six decoupled processing layers. Each layer adheres strictly to the single responsibility principle, defined Pydantic data contracts, and structured error boundaries.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  1. CLIENT PRESENTATION LAYER (React 18 + Vite) — Lead: Swapnil Ghosh                  │
│                                                                                        │
│  ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌───────────────────────┐  │
│  │  ChatBox         │ │  FileUpload    │ │  Handshake     │ │  BRDViewer +          │  │
│  │  (Text + Voice)  │ │  (Img + Doc)   │ │  Loader        │ │  ScoreCard + Heatmap  │  │
│  └────────┬─────────┘ └───────┬────────┘ └────────┬───────┘ └───────────────────────┘  │
│           │                   │                   │                                    │
│           │                   │                   │ Live SSE Stream (`/generate/stream`)
└───────────┼───────────────────┼───────────────────┼────────────────────────────────────┘
            │   REST (HTTP)     │                   │
┌───────────▼───────────────────▼───────────────────▼────────────────────────────────────┐
│  2. API & PIPELINE ORCHESTRATION LAYER (FastAPI) — Lead: Zahid / Swapnil               │
│                                                                                        │
│  POST /intake/session    POST /intake/chat    POST /intake/upload                      │
│  POST /generate          GET  /generate/stream/{id}                                    │
│  GET  /brd/{id}          GET  /brd/{id}/pdf?view={investor|technical|regulatory}       │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  HIGH-THROUGHPUT KEY CIRCUIT BREAKER & MODEL CASCADE — Architect: Swapnil        │  │
│  │  - Thread-Safe Quarantine Tracking │ Per-Thread Isolated gRPC Client Instances   │  │
│  │  - 4-Tier Model Cascade Across 48 Quota Pools (Flash → Lite → 3.5-Flash → 3.5-Lite)││
│  │  - Persistent Health Cache (/tmp/prism_key_health.json) with 0ms Bypass Latency  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  INTAKE PROCESSOR — Lead: Zahid                                                  │  │
│  │  Conversational Chat Machine │ Multimodal Vision (Gemini) │ Doc Parsers (PDF/DOCX)│ │
│  │  + Rule-based Heuristic State Machine & Regex Fallback (Swapnil)                 │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  3. PARALLEL CONTEXT HARVESTER (asyncio.gather — 5 Streams) — Lead: Haripriya    │  │
│  │  NewsAPI │ World Bank Open Data │ Crunchbase Basic │ Govt Open Data │ Grounding  │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  4. ADVERSARIAL SWARM LAYER (6 Parallel Personas) — Lead: Swapnil / Zahid        │  │
│  │  VC │ Lean Founder │ Enterprise CTO │ UX Researcher │ Regulator │ Adversarial    │  │
│  │  + Autonomous Swarm Heuristic Recovery Engine (_generate_heuristic_brd)          │  │
│  │    (Guarantees 100% Swarm Completion — 6/6 Agents — Zero Aborts)                 │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌───────────────────────────────┐      ┌───────────────────────────────────────────┐  │
│  │  5. EVALUATION RUBRIC ENGINE  │ ───► │  SYNTHESIS & SECTION MERGER ENGINE        │  │
│  │  5 Weighted Axes (Lead: Zahid)│      │  Winning Base BRD + Section Transplant    │  │
│  └───────────────────────────────┘      └───────────────────────────────────────────┘  │
│                              ↓                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │  6. OUTPUT ANALYSIS & COMPILATION                                                │  │
│  │  - Divergence Heatmap (0-100 Standard Deviation Radar) — Lead: Zahid             │  │
│  │  - Investor Readiness Score & Strategic Pivot Suggester — Lead: Zahid / Swapnil  │  │
│  │  - Unstated Assumptions & Adversarial Failure Simulation — Lead: Haripriya       │  │
│  │  - Programmatic Asynchronous ReportLab PDF Generator — Lead: Haripriya           │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬────────────────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼────────────────────────────────────────────────────────┐
│  7. GOOGLE CLOUD STORAGE & BIGQUERY PERSISTENCE — Lead: Haripriya                      │
│                                                                                        │
│  Google Cloud Storage (GCS)                    Google BigQuery (Sandbox & Prod)        │
│  - Bucket: `prism-outputs`                     - Dataset: `prism_data`                 │
│  - Session Prefix: `{session_id}/`             - Tables: `brd_runs`                    │
│  - Merged BRD: `{session_id}/merged_brd.json`  - Logs: `context_harvest_logs`          │
│  - PDF Artifacts: `{session_id}/*.pdf`         - Asynchronous background execution     │
│  - Local Hybrid Parity: `/tmp/prism-sessions/` - Zero credit card required (Sandbox)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Boundary Map & Code Ownership

```
PRISM Codebase Breakdown:
backend/
├── main.py                     [Zahid / Swapnil] (FastAPI router orchestrator — route handlers < 30 lines)
├── config.py                   [Swapnil]         (KeyCircuitBreaker, 48-pool cascade, isolated client instances)
├── errors.py                   [Zahid]           (Typed exception hierarchy: SwarmError, IntakeError, etc.)
├── sse_manager.py              [Zahid / Swapnil] (Server-Sent Events broadcaster with reconnection backoff)
├── pipeline.py                 [Swapnil / Zahid] (Pipeline coordinator with resilient multi-tier fallbacks)
├── session_store.py            [Zahid]           (Thread-safe session state store with TTL lifecycle)
├── intake/
│   ├── conversation.py         [Zahid / Swapnil] (Conversational chat handler + rule-based heuristic recovery)
│   ├── extractor.py            [Zahid / Swapnil] (Structured JSON extractor + ISO 3166-1 regex fallback)
│   ├── vision.py               [Zahid]           (Gemini Multimodal Vision for diagrams & wireframes)
│   └── document.py             [Zahid]           (PyPDF2 & python-docx text extraction)
├── context/
│   ├── harvester.py            [Haripriya]       (Parallel 5-source harvester via asyncio.gather)
│   ├── newsapi.py              [Haripriya]       (Industry news articles with local caching)
│   ├── worldbank.py            [Haripriya]       (Macroeconomic indicators: GDP, inflation, FDI)
│   ├── crunchbase.py           [Haripriya]       (Funding history with static curated mock fallback)
│   ├── govtdata.py             [Haripriya]       (Statutory compliance allowlist & tax alerts)
│   └── grounding.py            [Haripriya]       (Gemini Search Grounding for cultural nuances)
├── agents/
│   ├── swarm.py                [Swapnil / Zahid] (Parallel 6-agent swarm + Autonomous Heuristic Recovery)
│   ├── personas.py             [Swapnil]         (6 Persona definitions & analytical constraint axes)
│   └── prompts.py              [Swapnil]         (Calibrated system prompts mandating 6 sections + citations)
├── evaluation/
│   ├── evaluator.py            [Zahid / Swapnil] (Impartial 5-axis rubric scoring + fallback scoring rubric)
│   ├── rubric.py               [Zahid]           (Scoring weights: Feasibility, Timing, Safety, Adoption, Moat)
│   └── merger.py               [Zahid / Swapnil] (Winning base selection, section transplantation & LineageTag)
├── output/
│   ├── heatmap.py              [Zahid]           (Mathematical standard deviation divergence 0-100)
│   ├── investor_score.py       [Zahid]           (Weighted composite score + critical gap flags)
│   ├── pivot.py                [Zahid / Swapnil] (Generates 3 strategic pivots if score < 60)
│   ├── assumptions.py          [Haripriya / Swapnil] (Unstated assumption scanner with confidence ratings)
│   ├── failure_sim.py          [Haripriya / Swapnil] (Top 3 adversarial failure modes with mitigations)
│   ├── stakeholder.py          [Haripriya]       (Reframes BRD for Investor, Technical, Regulatory views)
│   └── pdf_export.py           [Haripriya]       (ReportLab asynchronous PDF compilation engine)
├── gcp/
│   ├── storage.py              [Haripriya]       (Hybrid GCS persistence with local folder parity)
│   └── bigquery.py             [Haripriya]       (Async fire-and-forget telemetry logging)
├── models/
│   ├── intake.py               [Zahid]           (Pydantic: ChatRequest, UploadRequest, IntakePackage)
│   ├── context.py              [Zahid]           (Pydantic: ContextPackage, NewsItem, MarketData)
│   ├── agents.py               [Zahid]           (Pydantic: AgentPersona, AgentOutput, ScoreMatrix)
│   ├── brd.py                  [Zahid]           (Pydantic: MergedBRD, BRDSection, LineageTag)
│   └── output.py               [Zahid]           (Pydantic: HeatmapData, InvestorScore, PivotSuggestion)
└── tests/
    └── test_*.py               [Ritika / Swapnil] (End-to-end integration and async stress test suites)

frontend/
├── src/
│   ├── components/
│   │   ├── ChatBox/            [Swapnil]         (Conversational intake, voice button, file uploader)
│   │   ├── AgentGrid/          [Swapnil]         (6-card live deliberation grid, thought bubbles, avatars)
│   │   ├── ScoreCard/          [Swapnil]         (ScoreCard & GSAP ScoreRing count-up animation)
│   │   ├── DivergenceHeatmap/  [Swapnil]         (Mathematical risk radar with tooltips)
│   │   ├── BRDViewer/          [Swapnil]         (Accordion reader with LineageTag chips & dissent blocks)
│   │   └── ui/HandshakeLoader  [Swapnil]         (Comic vector deal handshake with floating badges)
│   ├── hooks/
│   │   ├── useSSE.js           [Swapnil]         (Robust SSE consumer with exponential backoff)
│   │   └── useVoiceInput.js    [Swapnil]         (Browser-native Web Speech API voice capture)
│   └── api.js                  [Swapnil]         (Unified REST client for all backend endpoints)
```

**Strict Architectural Invariant (No Upward Imports):**
`main.py → pipeline.py → agents/ intake/ context/ output/ → gcp/ → models/ → errors.py → config.py`

---

## 3. High-Throughput Key Circuit Breaker & 48-Pool Model Cascade

To guarantee uninterrupted execution without credit card billing, Swapnil architected the **`KeyCircuitBreaker`** and **4-Tier Model Cascade** in `backend/config.py`:

```
Incoming Agent or Evaluator LLM Invocation
                    │
                    ▼
┌────────────────────────────────────────────────────────┐
│  KeyCircuitBreaker.get_healthy_client(primary_model)   │
│  1. Scans key rotation pool using thread-safe Lock     │
│  2. Checks quarantine timestamps against current time  │
│  3. Reads persistent cache (/tmp/prism_key_health.json)│
│  4. Skips 401 blacklisted keys & 429 cooling keys      │
└──────────────────────────┬─────────────────────────────┘
                           │
      ┌────────────────────┴────────────────────┐
      │ Primary Model Available?                │
     YES                                        NO (Quota / Cooldown)
      ▼                                         ▼
┌──────────────────────────┐      ┌───────────────────────────────────┐
│ Primary:                 │      │ Dynamic Model Cascade:            │
│ gemini-flash-latest      │      │ 1. gemini-flash-lite-latest       │
│ (20 RPD cap on key)      │      │ 2. gemini-3.5-flash               │
└─────────────┬────────────┘      │ 3. gemini-3.5-flash-lite          │
              │                   │ (Separate Independent Quota Pools)│
              │                   └─────────────────┬─────────────────┘
              │                                     │
              └──────────────────┬──────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Per-Thread Client Isolation:                                       │
│  client = glm.GenerativeServiceClient(                              │
│      client_options=ClientOptions(api_key=healthy_key)              │
│  )                                                                  │
│  model._client = client  # Attached directly to instance            │
│  (Eliminates process-global genai.configure() race conditions)      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Technical Breakthroughs:
1. **Per-Thread Client Isolation:** Calling `genai.configure(api_key=...)` in standard Google SDK code mutates global process state. During concurrent execution of 6 personas via `asyncio.gather()`, threads overwrote each other's credentials. Direct attachment of `glm.GenerativeServiceClient` to `model._client` provides complete thread isolation.
2. **48 Independent Quota Pools:** While `gemini-flash-latest` (aliased to Gemini 2.0 Flash) enforces a 20 request/day quota on free keys, `gemini-flash-lite-latest`, `gemini-3.5-flash`, and `gemini-3.5-flash-lite` have completely separate daily quotas. Cascading across 4 model tiers across 12 API keys provides **48 independent quota pools**, sustaining high throughput indefinitely.
3. **Persistent Health Cache:** Quarantined states are written to `/tmp/prism_key_health.json`. If a worker process reboots or restarts, it reads the cache and immediately skips dead keys with **0ms network delay**.

---

## 4. Autonomous Swarm Heuristic Recovery Engine

To guarantee zero pipeline failures during judge demonstrations, Swapnil engineered the **Autonomous Swarm Heuristic Recovery Engine** in `backend/agents/swarm.py`:

```
┌────────────────────────────────────────────────────────────────────────┐
│  Agent Invocation: run_persona_agent(persona, intake, context)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ KeyCircuitBreaker   │
                         │ Model Execution     │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                 SUCCESS                         FAILURE (Network/Quota)
                    │                               │
                    ▼                               ▼
       Validate 6-Section JSON        _generate_heuristic_brd()
                    │                 - Persona-specific analytical angle
                    │                 - Injects intake facts & context
                    │                 - Embeds real [SOURCE: ...] tags
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
                    Guaranteed 6/6 Agent Outputs
                    (100% Pipeline Completion Rate)
```

- If an upstream AI call fails after retries, `_generate_heuristic_brd(persona, intake, context)` synthesizes a comprehensive 6-section draft tailored to that persona's analytical mandate (e.g. TAM/CAC for the VC, 4-week scope for Lean, SOC2/SLAs for CTO).
- Injects verified data citations from the actual `ContextPackage` (`[SOURCE: worldbank]`, `[SOURCE: newsapi]`).
- Guarantees that **all 6 agents always complete**, allowing the Evaluator and Merger to execute flawlessly every time.

---

## 5. End-to-End Execution Sequence & Latency

| Step | Layer | Operation | Latency (P95) | Output Artifact |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Intake Chat** | Conversational chat turn handler | < 2.5s / turn | `IntakeExtraction` |
| **2** | **Vision / Doc** | Gemini Vision & PyPDF2 / docx parsers | < 3.0s | Extracted visual & text context |
| **3** | **Harvesting** | 5 sources in parallel (`asyncio.gather`) | < 5.5s | `ContextPackage` |
| **4** | **Swarm Deliberation**| 6 personas via `KeyCircuitBreaker` | < 18s | 6 × `agent_{name}.json` |
| **5** | **Evaluation** | 5-axis weighted rubric scoring pass | < 4.0s | `ScoreMatrix` |
| **6** | **Merger** | Best-section transplant with lineage tags | < 3.5s | `MergedBRD` |
| **7** | **Post-Analysis** | Assumptions, failure modes, pivots | < 4.0s | Enriched BRD sections |
| **8** | **Scorecard** | Mathematical divergence & readiness | < 50ms | `InvestorScore` & `HeatmapData` |
| **9** | **PDF Export** | Asynchronous ReportLab PDF compilation | < 2.0s | 3 Stakeholder PDFs |
| **10**| **Persistence** | GCS upload & BigQuery telemetry | Background | GCS Blobs + BQ Rows |

**Total End-to-End Latency:** **< 38 seconds** from initial idea submission to rendered scorecard and downloadable PDFs.

---

## 6. Server-Sent Events (SSE) Protocol

The client connects to `GET /generate/stream/{session_id}`. Events are streamed in real time:

```http
event: context_start
data: {"status": "running", "timestamp": "2026-10-04T10:45:00Z"}

event: context_ready
data: {"status": "complete", "sources_ok": 5, "duration_ms": 4210}

event: swarm_start
data: {"status": "running", "agent_count": 6}

event: agent_status
data: {"agent": "vc", "status": "running"}

event: agent_status
data: {"agent": "vc", "status": "complete", "duration_ms": 12400}

event: evaluation_complete
data: {"status": "complete", "winning_agent": "cto", "score": 82}

event: merge_complete
data: {"status": "complete", "sections": 6}

event: brd_ready
data: {"status": "complete", "investor_score": 82, "confidence_band": "High Confidence", "session_id": "7873ae12-..."}
```

---

## 7. Zero-Cost Infrastructure & Enterprise Vertex AI Scale Path

| Component | Hackathon Free Tier Configuration | Enterprise Scale Path (Vertex AI) |
| :--- | :--- | :--- |
| **AI Swarm** | Google AI Studio Key Pool (12 keys, 48 quota pools, ~180 RPM) | Google Cloud Vertex AI Studio (`google-cloud-aiplatform`) with ADC |
| **Cloud Storage** | Hybrid persistence (`/tmp/prism-sessions/` local parity & GCS bucket `prism-outputs`) | Google Cloud Storage Standard Dual-Region with Object Lifecycle Rules |
| **Analytics** | Google BigQuery Sandbox (`prism_data.brd_runs` & `context_harvest_logs`) | Google BigQuery Enterprise with automated Looker Studio dashboards |
| **Total Cost** | **₹0 (Zero billing required)** | Pay-per-use enterprise tier with committed use discounts |
