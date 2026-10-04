<p align="center">
  <img src="./docs/images/logo.jpg" alt="PRISM Logo" width="220" style="border-radius: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.5);" />
</p>

# PRISM 🔺
### *One Idea. Six Perspectives. One Ground Truth.*

<p align="center">
  <img src="https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini 2.0 Flash" />
  <img src="https://img.shields.io/badge/Google_Cloud-Storage_%26_BigQuery-34A853?style=for-the-badge&logo=googlecloud&logoColor=white" alt="GCP Storage & BigQuery" />
  <img src="https://img.shields.io/badge/FastAPI-Async_Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React_18-Vite_Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/Architecture-Resilient_Key_Pool-7C3AED?style=for-the-badge&logo=speedtest&logoColor=white" alt="Key Pool" />
  <img src="https://img.shields.io/badge/Cost_Tier-%E2%82%B90_Zero_Billing-00D68F?style=for-the-badge&logo=cashapp&logoColor=white" alt="Zero Cost" />
  <img src="https://img.shields.io/badge/Hackathon-Manipal_2026-EA4335?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Manipal Hackathon 2026" />
</p>

<p align="center">
  <img src="./docs/images/prism_swarm_lineup.jpg" alt="PRISM 6-Agent Swarm Lineup" width="100%" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

> **PRISM** is an enterprise-grade multi-modal AI decision system that transforms raw, fragmented business ideas (text, voice, wireframes, and documents) into institutional-grade, investor-ready Business Requirements Documents (BRDs). 
> 
> Rather than relying on a single one-shot prompt that produces agreeable hallucinations, PRISM executes a **Structured Disagreement Engine** — routing the idea through a parallel swarm of six adversarial AI expert personas, grounding claims in live market data, evaluating tension on a 5-axis rubric, and delivering explainable decisions with full line-by-line lineage attribution.

---

## 📑 Table of Contents

- [The Core Philosophy](#-the-core-philosophy)
- [Hackathon Problem Statement & Delivery](#-hackathon-problem-statement--delivery)
- [The 6-Agent Adversarial Swarm](#-the-6-agent-adversarial-swarm)
- [High-Throughput Key Circuit Breaker & 48-Pool Cascade](#-high-throughput-key-circuit-breaker--48-pool-cascade)
- [System Architecture & Data Flow](#-system-architecture--data-flow)
- [Visual Highlights & UI Walkthrough](#-visual-highlights--ui-walkthrough)
- [End-to-End Pipeline Walkthrough](#-end-to-end-pipeline-walkthrough)
- [API Reference & Event Stream Protocol](#-api-reference--event-stream-protocol)
- [Quickstart Guide](#-quickstart-guide)
- [Environment Configuration](#-environment-configuration)
- [Team & Roles](#-team--roles)

---

## 🌟 The Core Philosophy

Traditional AI tools generate agreeable, generic PRDs that collapse under technical scale, regulatory audits, or cutthroat competition. PRISM replaces passive autocomplete with **simultaneous institutional scrutiny**:

```
                              ┌────────────────────────┐
                              │  Raw Fragmented Idea   │
                              │ (Text, Voice, Img, Doc)│
                              └───────────┬────────────┘
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │   Real-Time Multi-Source Context Harvest    │
                   │ (NewsAPI, World Bank, Crunchbase, Grounding)│
                   └──────────────────────┬──────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
       💜 The VC                 🩵 Lean Founder                💚 Enterprise CTO
   (10x Scale & Moat)          (4-Week MVP Simplicity)        (Uptime, Security, SLAs)
            ▲                             ▲                             ▲
            ├─────────────────────────────┼─────────────────────────────┤
            ▼                             ▼                             ▼
     🧡 UX Researcher              💙 The Regulator             ❤️ The Adversarial
(Friction & Habit Loops)        (GDPR/DPDP & Liability)      (Competitor Attack Vectors)
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                               ┌──────────▼──────────┐
                               │  Rubric Evaluation  │
                               │   & Section Merge   │
                               └──────────┬──────────┘
                                          │
               ┌──────────────────────────┴──────────────────────────┐
               ▼                                                     ▼
    Divergence Heatmap &                                  3 Stakeholder PDF Exports
  Investor Readiness Score                             (Investor / Tech / Regulatory)
```

---

## 🏆 Hackathon Problem Statement & Delivery

### The Official Challenge:
> *"Build a scalable, multi-modal AI system using Google Gemini AI and integrated Google Cloud tools (such as Vertex AI, Cloud Storage, and BigQuery) that can process real-time, fragmented data (text, images, and documents) and deliver accurate, context-aware, and explainable decisions in complex and dynamic environments."*

### How PRISM Delivers:

| Requirement | PRISM Implementation | Zero-Cost Infrastructure |
| :--- | :--- | :--- |
| **Scalable Multi-Modal AI** | Ingests unformatted text, speech ([Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)), wireframes/diagrams ([Gemini Multimodal Vision](https://ai.google.dev/)), and pitch decks ([PyPDF2](https://pypi.org/project/PyPDF2/), [python-docx](https://python-docx.readthedocs.io/)). | 100% free with browser-native APIs and Gemini 2.0 Flash. |
| **Real-Time Fragmented Data** | Parallel context harvester simultaneously queries NewsAPI, World Bank Open Data, Crunchbase, and Gemini Search Grounding. | Open REST endpoints + intelligent in-memory regional caching. |
| **Accurate, Explainable Decisions** | 5-axis rubric scoring (`evaluator.py`), section transplantation (`merger.py`), mathematical divergence variance (`heatmap.py`), and lineage attribution (`[SOURCE: ...]`). | Strict mathematical computation and deterministic JSON parsing. |
| **Integrated Google Cloud Tools** | **Gemini AI Studio Pool** (~180 RPM free) with Vertex AI compatibility shim; **Google Cloud Storage** for multimodal blobs & PDFs; **Google BigQuery** for decision audit logs. | **₹0 forever** utilizing GCP Free Tier and BigQuery Sandbox. |

---

## 👥 The 6-Agent Adversarial Swarm

Each persona runs in parallel on an isolated Gemini instance with strict system prompt boundaries:

<p align="center">
  <img src="./docs/images/prism_agent_portraits.jpg" alt="PRISM Agent Portraits" width="90%" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

| Portrait | Persona | Accent Token | Focus & Hard Constraints |
| :---: | :--- | :--- | :--- |
| <img src="./docs/images/agents/agent_vc.jpg" width="56" style="border-radius: 8px;" /> | **The VC** | `Violet (#7C3AED)` | **Venture Scale & Defensibility:** Demands 10x scalability, TAM/SAM/SOM expansion, high gross margins, and network effect moats. Rejects incremental tools. |
| <img src="./docs/images/agents/agent_lean.jpg" width="56" style="border-radius: 8px;" /> | **The Lean Founder** | `Sky Blue (#0EA5E9)` | **Speed to Market & Capital Efficiency:** Ruthlessly strips non-essential scope to mandate a 4-week validation MVP build within budget runway. |
| <img src="./docs/images/agents/agent_cto.jpg" width="56" style="border-radius: 8px;" /> | **The Enterprise CTO** | `Emerald (#10B981)` | **Scalability, Security & SLAs:** Audits high-availability cloud architecture (GCP, BigQuery, GCS), zero-trust networking, microservices, and 99.95% uptime guarantees. |
| <img src="./docs/images/agents/agent_ux.jpg" width="56" style="border-radius: 8px;" /> | **The UX Researcher** | `Amber (#F59E0B)` | **Human-Centered Adoption:** Eliminates cognitive onboarding friction, models time-to-value, user habit loops, and WCAG accessibility standards. |
| <img src="./docs/images/agents/agent_regulator.jpg" width="56" style="border-radius: 8px;" /> | **The Regulator** | `Indigo (#6366F1)` | **Statutory Compliance & Legal Rigor:** Enforces data residency, GDPR/DPDP privacy mandates, licensing requirements, and audits consumer liability risks. |
| <img src="./docs/images/agents/agent_adversarial.jpg" width="56" style="border-radius: 8px;" /> | **The Adversarial** | `Crimson (#EF4444)` | **Stress-Testing & Vulnerability Simulation:** Simulates hostile competitor retaliation, economic churn triggers, API cost blowouts, and exploits weak assumptions. |

---

## 🛡️ High-Throughput Key Circuit Breaker & 48-Pool Cascade

Google Gemini AI Studio keys on the free tier provide 15 RPM, with certain models capping at 20 requests/day per key. PRISM implements an **Intelligent Circuit Breaker and Model Cascade Engine** ([backend/config.py](file:///home/swapnilg/Code%20With%20Swap/PRISM/Prism/backend/config.py)):

```
Incoming Agent Invocation
          │
          ▼
┌────────────────────────────────────────────────────────┐
│  KeyCircuitBreaker (Thread-Safe Selection & Isolation) │
│  - Tracks per-key & per-model cooldown timestamps      │
│  - Instant bypass of blacklisted (401) or 429 keys     │
│  - Persistent health state cache (/tmp/prism_key_health)│
└──────────────────────────┬─────────────────────────────┘
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
   Primary Model                      Fallback Models (Separate Quota Pools)
 gemini-flash-latest            gemini-flash-lite-latest ──► gemini-3.5-flash
 (20 RPD cap on key)            (Unrestricted separate RPM / Daily Quota)
          │                                 │
          └────────────────┬────────────────┘
                           ▼
          Per-Thread Isolated gRPC Client
          glm.GenerativeServiceClient(api_key=key)
          (Zero global genai.configure race conditions)
```

- **Per-Thread Client Isolation:** Prevents global state race conditions during 6-way concurrent agent execution by provisioning isolated `glm.GenerativeServiceClient` instances directly to `model._client`.
- **4-Tier Model Cascade Across 48 Quota Pools:** When `gemini-flash-latest` hits its daily quota on a key, the request automatically cascades to `gemini-flash-lite-latest` &rarr; `gemini-3.5-flash` &rarr; `gemini-3.5-flash-lite`. With 12 configured keys, PRISM operates across **48 independent quota pools**.
- **Persistent State Cache:** Quarantined states are saved to `/tmp/prism_key_health.json`, allowing fresh processes to bypass exhausted keys with **0ms network delay**.
- **Autonomous Swarm Heuristic Recovery:** If upstream network failure occurs, `_generate_heuristic_brd` immediately produces a complete, persona-grounded draft, guaranteeing a **100% completion rate (6/6 agents)** with zero pipeline aborts.

---

## 🏛️ System Architecture & Data Flow

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER (React 18 + Vite)                                                        │
│  - ChatBox (Voice & Text)   - FileUpload (PDF, DOCX, PNG)   - HandshakeLoader          │
│  - AgentGrid (Live SSE)     - DivergenceHeatmap (GSAP)      - BRDViewer & ScoreCard    │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ REST & SSE Stream
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│  FASTAPI ORCHESTRATION LAYER (backend/main.py & pipeline.py)                           │
│                                                                                        │
│  1. Intake Processor: Multi-turn chat turn handler + rule-based heuristic fallback    │
│  2. Context Harvester: 5 parallel streams via asyncio.gather()                        │
│  3. Swarm Layer: 6 parallel persona agents with KeyCircuitBreaker                     │
│  4. Evaluator & Merger: Rubric scoring + surgical section transplantation             │
│  5. Post-Merge Analysis: Assumption flags, failure modes, strategic pivots             │
│  6. PDF Compiler: Asynchronous ReportLab PDF generation for 3 stakeholder views       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
┌───────────────────────────────────────────▼────────────────────────────────────────────┐
│  GOOGLE CLOUD STORAGE & BIGQUERY PERSISTENCE                                           │
│  - GCS Bucket: `prism-outputs/{session_id}/agent_*.json`, `merged_brd.json`, `*.pdf`   │
│  - BigQuery Dataset: `prism_data.brd_runs` & `prism_data.context_harvest_logs`        │
│  - Local Hybrid Parity: Strict GCS directory parity in `/tmp/prism-sessions/`          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visual Highlights & UI Walkthrough

### 1. Comic Vector Handshake Loader (`HandshakeLoader.jsx`)
<p align="center">
  <img src="./docs/images/handshake_loader.png" alt="PRISM Handshake Deal Loader" width="480" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

During swarm deliberation and context harvesting, PRISM renders a custom comic-styled handshake animation symbolizing the founder closing a deal with the market. Surrounded by floating badges (`$`, `%`, `♥`, `✔`, `📈`) on independent sinusoidal floating curves.

### 2. Live Agent Deliberation Grid (`AgentGrid.jsx`)
<p align="center">
  <img src="./docs/images/generation_page_view.png" alt="PRISM Live Agent Deliberation Grid" width="100%" style="border-radius: 12px; border: 1px solid #1E3A5F;" />
</p>

Each persona features a dedicated archetype avatar, live status chip (`queued` &rarr; `running` &rarr; `complete`), pulse border, and live deliberation thought bubbles displaying what the agent is currently debating in real time.

### 3. Visual Divergence Heatmap (`DivergenceHeatmap.jsx`)
Calculates standard deviation across all 6 agent rubric scores per section, rendering an interactive risk radar from Green (Consensus) to Amber (Contested) to Red (High Disagreement) with interactive tooltips detailing dissenting views.

### 4. Interactive Investor Readiness Ring (`ScoreRing.jsx`)
GSAP-orchestrated count-up SVG ring displaying a 0–100 composite score, categorized by confidence bands (`High Confidence`, `Promising`, `Critical Gaps`).

---

## 🔄 End-to-End Pipeline Walkthrough

| Step | Component | Method / Operation | Latency (P95) | Output Artifact |
| :---: | :--- | :--- | :---: | :--- |
| **1** | **Intake Chat** | Multi-turn conversational turn handler | < 2.5s | Structured `IntakeExtraction` |
| **2** | **Vision / Doc** | Gemini Vision & PyPDF2 / docx parsers | < 3.0s | Extracted visual & text context |
| **3** | **Harvesting** | 5 sources in parallel (`asyncio.gather`) | < 5.5s | `ContextPackage` |
| **4** | **Swarm Deliberation**| 6 personas via `KeyCircuitBreaker` | < 18s | 6 × `agent_{name}.json` |
| **5** | **Evaluation** | 5-axis weighted rubric scoring pass | < 4.0s | `ScoreMatrix` |
| **6** | **Merger** | Best-section transplant with lineage tags | < 3.5s | `MergedBRD` |
| **7** | **Post-Analysis** | Assumptions, failure modes, pivots | < 4.0s | Enriched BRD sections |
| **8** | **Scorecard** | Mathematical divergence & readiness | < 50ms | `InvestorScore` & `HeatmapData` |
| **9** | **PDF Export** | Asynchronous ReportLab PDF compilation | < 2.0s | 3 Stakeholder PDFs |
| **10** | **Persistence** | GCS upload & BigQuery telemetry | Background | GCS Blobs + BQ Rows |

---

## 📡 API Reference & Event Stream Protocol

### Core Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/intake/session` | Creates a new session UUID and initializes state store. |
| `POST` | `/intake/chat` | Conducts a conversational intake turn; returns next question or `is_complete`. |
| `POST` | `/intake/upload` | Uploads and processes PDF, DOCX, JPEG, or PNG files (max 10MB). |
| `POST` | `/generate` | Launches background 6-agent swarm pipeline. |
| `GET` | `/generate/stream/{id}` | Real-time Server-Sent Events (SSE) progress stream. |
| `GET` | `/brd/{id}` | Retrieves final merged BRD, lineage tags, score, and heatmap. |
| `GET` | `/brd/{id}/pdf?view={view}` | Downloads compiled PDF for `investor`, `technical`, or `regulatory` view. |

### SSE Event Stream Example (`/generate/stream/{id}`)

```http
event: context_start
data: {"status": "running"}

event: context_ready
data: {"status": "complete", "sources_ok": 5}

event: swarm_start
data: {"status": "running"}

event: agent_status
data: {"agent": "vc", "status": "running"}

event: agent_status
data: {"agent": "vc", "status": "complete"}

event: evaluation_complete
data: {"status": "complete", "winning_agent": "vc"}

event: merge_complete
data: {"status": "complete"}

event: brd_ready
data: {"status": "complete", "investor_score": 78, "confidence_band": "High Confidence", "sections": 6}
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Node.js:** v18.x or v20.x
- **Python:** v3.11, v3.12, v3.13, or v3.14
- **Git**

### 2. Clone & Install Frontend
```bash
git clone https://github.com/Haripriya24071/Prism.git
cd Prism/frontend
npm install
npm run dev
# Frontend running at http://localhost:5173
```

### 3. Setup Backend Environment
```bash
# In the Prism root directory:
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to both root `.env` and `backend/.env`:
```bash
cp .env.example backend/.env
cp .env.example .env
```
Populate your Gemini API keys (at least 1 key from [Google AI Studio](https://aistudio.google.com/app/apikey)):
```env
GEMINI_API_KEY_1=your_ai_studio_key_here
GEMINI_FLASH_MODEL=gemini-flash-latest
GEMINI_PRO_MODEL=gemini-flash-latest
```

### 5. Launch Backend
```bash
uvicorn backend.main:app --reload --port 8000
# API docs available at http://localhost:8000/docs
```

---

## ⚙️ Environment Configuration

```env
# ── Gemini Multi-Key Pool (100% Free Tier) ──
GEMINI_API_KEY_1=AQ.Ab8RN6JX_...
GEMINI_API_KEY_2=AQ.Ab8RN6L6_...
GEMINI_FLASH_MODEL=gemini-flash-latest
GEMINI_PRO_MODEL=gemini-flash-latest

# ── Google Cloud Infrastructure ──
GCP_PROJECT_ID=prism-hackathon-510523
GCP_REGION=us-central1
GCS_BUCKET_NAME=prism-outputs
BIGQUERY_DATASET=prism_data
GOOGLE_APPLICATION_CREDENTIALS=./prism-hackathon-key.json

# ── External Intelligence APIs (Optional) ──
NEWSAPI_KEY=
CRUNCHBASE_KEY=

# ── Application Runtime ──
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
SESSION_TTL_SECONDS=7200
MAX_UPLOAD_BYTES=10485760
LOG_LEVEL=INFO
ENV=development
```

---

## 👥 Team & Roles

| Contributor | Role | Core Contributions |
| :--- | :--- | :--- |
| **Swapnil Ghosh** | **Frontend Lead & Full-Stack Architect** | React 18 UI, HandshakeLoader comic vector animation, live AgentGrid avatars & thought bubbles, ScoreRing GSAP count-up, Divergence Heatmap, SSE stream consumer, KeyCircuitBreaker engine, Swarm Heuristic Recovery engine, pipeline resilience, end-to-end async test suites. |
| **Zahid** | **Backend Core & AI Orchestration** | FastAPI orchestrator, Pydantic v2 schemas, typed error boundaries, multi-turn conversational intake handler, evaluation rubric engine, and surgical section merger. |
| **Haripriya** | **Integrations, Storage & BigQuery** | Parallel Context Harvester (NewsAPI, World Bank, Crunchbase, Grounding), Google Cloud Storage hybrid persistence, BigQuery sandbox audit logging, and ReportLab PDF compilation. |
| **Ritika** | **QA, Pitch Deck & Demo Lead** | Test fixtures, end-to-end latency validation, Hackathon Pitch Deck (PPT), demo rehearsal script (Fundable SaaS vs High-Risk Pivot), and fallback video recording. |

---

## 📄 License
MIT License. Built with passion for the **Manipal Hackathon 2026**.


---

## Backend Setup (Local Dev)

### Prerequisites
- Python 3.11+
- A Google Cloud project with Vertex AI API enabled
- A GCP service account JSON key with roles: `Vertex AI User`, `Storage Object Admin`, `BigQuery Data Editor`

### 1. Clone and branch
```bash
git clone https://github.com/Haripriya24071/Prism.git
cd Prism
git checkout main
git pull
```

### 2. Create virtual environment
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env and set:
# GCP_PROJECT_ID=your-real-project-id
# GCP_REGION=us-central1
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# GCS_BUCKET_NAME=prism-sessions
# BIGQUERY_DATASET=prism_data
# NEWSAPI_KEY=your-key      (optional — static fallback used if absent)
# CRUNCHBASE_KEY=your-key   (optional — static fallback used if absent)
```

### 4. Start the backend
```bash
uvicorn main:app --reload --port 8000
```
Visit `http://localhost:8000/health` — should return `{"status":"ok","version":"0.1.0"}`.

### 5. Run tests
```bash
python -m pytest tests/ -v
```
Expected: 129 passed.

### 6. Demo dry-run (night before hackathon)
```bash
# Pre-warm NewsAPI cache
python demo_runner.py --prewarm

# Run a full scenario dry-run (requires real GCP credentials)
python demo_runner.py IndiaFintechSMB
python demo_runner.py SingaporeEdTechB2B
python demo_runner.py USHealthTechConsumer
```

### API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/intake/session` | Create session |
| GET | `/intake/session/{id}` | Get session status |
| POST | `/intake/chat` | Conversation turn |
| POST | `/intake/upload` | Upload file (PDF/DOCX/image) |
| POST | `/generate` | Start BRD generation |
| GET | `/generate/stream/{id}` | SSE live progress stream |
| GET | `/brd/{id}` | Get completed BRD |
| GET | `/brd/{id}/pdf?view=investor` | Get PDF signed URL |

### Architecture Notes
- All Gemini calls go through **Vertex AI** (`google-cloud-aiplatform` SDK) — no direct API key rotation.
- In dev mode (`ENV=development`): GCS writes go to `/tmp/prism-sessions/`, BigQuery logging is skipped.
- Crunchbase and NewsAPI have static fallbacks — the pipeline runs without these keys.
- PDF filenames: `output_investor.pdf`, `output_technical.pdf`, `output_regulatory.pdf` (per SCHEMA.md).
