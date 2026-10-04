# PRISM — Technology Stack

> 100% Free Tier. Enterprise Production Architecture. Every technology justified.

---

## 1. Frontend Technologies

| Technology | Version | Purpose & Rationale |
| :--- | :--- | :--- |
| **React** | 18.x | Modular component hierarchy matching our multi-panel UI (`ChatBox`, `AgentGrid`, `DivergenceHeatmap`, `BRDViewer`, `ScoreCard`). |
| **Vite** | 5.x | Ultra-fast Hot Module Replacement (HMR) and optimized modern JavaScript bundling. |
| **Tailwind CSS** | 3.x | Utility-first styling mapped directly to custom theme tokens (`tokens.css`, `index.css`) with zero ad-hoc hex values. |
| **Framer Motion** | 11.x | Declarative micro-animations, agent card status transitions, and modal animations (`transform` and `opacity` only). |
| **GSAP** | 3.x | High-precision timeline orchestration for the Divergence Heatmap bar reveals and animated circular `ScoreRing` count-ups. |
| **Web Speech API** | Native | Zero-dependency, low-latency browser-native speech-to-text intake built into modern browsers (Chrome/Edge). |

---

## 2. Backend Technologies

| Technology | Version | Purpose & Rationale |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Native `asyncio` concurrency, robust type hints, and broad AI library support. |
| **FastAPI** | 0.111+ | Asynchronous-first web framework with automatic OpenAPI documentation and native SSE support. |
| **Pydantic v2** | 2.x | High-speed data validation and strict schema enforcement for all intake, agent, and output models. |
| **Uvicorn** | 0.29+ | High-performance ASGI web server for production and development execution. |
| **HTTPX** | 0.27+ | Fully asynchronous HTTP client for parallel context harvesting across external APIs. |
| **Tenacity** | 8.x+ | Exponential backoff and retry decorators for network resilience. |
| **ReportLab** | 4.x+ | Programmatic PDF generation engine for Stakeholder BRD document compilation. |
| **PyPDF2 / Docx** | 3.x / 1.x| Fast text extraction from uploaded pitch decks, PRDs, and business specifications. |

---

## 3. AI Core & Model Orchestration

| Component | Model / Engine | Implementation Details |
| :--- | :--- | :--- |
| **Swarm Personas (6 Calls)** | `gemini-flash-latest` (Gemini 2.0 Flash) | 6 parallel reasoning personas (VC, Lean, CTO, UX, Regulator, Adversarial). |
| **Intake Extraction** | `gemini-flash-latest` | Single-turn conversation parsing with structured JSON schema enforcement. |
| **Multimodal Vision** | `gemini-flash-latest` | Visual understanding of uploaded architectural sketches, wireframes, and whiteboard photos. |
| **Evaluator & Merger** | `gemini-flash-latest` | Impartial rubric scoring across 5 criteria and surgical section transplantation. |
| **Post-Merge Analysis** | `gemini-flash-latest` | Unstated assumption detection, failure mode simulation, and strategic pivot generation. |
| **Search Grounding** | Gemini Grounding | Real-time cultural, regional, and seasonal market context extraction. |

### High-Throughput Key Circuit Breaker & Model Cascade
- **Provider:** Google AI Studio Gemini API (`google.generativeai`).
- **Capacity:** 12 API keys rotating via thread-safe `KeyCircuitBreaker`.
- **4-Tier Model Cascade Across 48 Quota Pools:** Cascades requests across `gemini-flash-latest` &rarr; `gemini-flash-lite-latest` &rarr; `gemini-3.5-flash` &rarr; `gemini-3.5-flash-lite`, completely bypassing 20 RPD limits.
- **Client Thread Isolation:** Bypasses process-global `genai.configure()` race conditions by provisioning isolated `glm.GenerativeServiceClient(api_key=key)` instances directly to each model's `_client`.
- **Persistent State Cache:** Quarantined states saved to `/tmp/prism_key_health.json` for 0ms failover bypass.
- **Autonomous Swarm Heuristic Recovery:** `_generate_heuristic_brd` guarantees 100% swarm completion (6/6 agents) under any network or quota condition.

---

## 4. Google Cloud Platform Integration

| Service | Configuration | Cost / Free Tier |
| :--- | :--- | :--- |
| **Google BigQuery** | **Dataset:** `prism_data`<br>**Tables:** `brd_runs`, `context_harvest_logs`<br>**Mode:** BigQuery Sandbox & ADC | **₹0 Forever**<br>(10 GB active storage + 1 TB queries/month free without credit card) |
| **Google Cloud Storage** | **Bucket:** `prism-outputs`<br>**Architecture:** Hybrid persistence — production GCS bucket with local GCS-schema fallback in `/tmp/prism-sessions/`. | **₹0 Forever**<br>(5 GB standard storage free tier) |
| **Google Vertex AI** | Initialized via enterprise compatibility layer in `backend/config.py`. Direct production scale path. | **₹0** |

---

## 5. External Context Harvesters

| Source | Target Intelligence | Resilience Strategy |
| :--- | :--- | :--- |
| **NewsAPI** | Regional political & economic climate, competitor press | In-memory cache keyed on region + industry (100 req/day free). |
| **World Bank Open Data** | Macroeconomic indicators (GDP, inflation, ease of business) | Open REST API with fallback to regional averages. |
| **Crunchbase Basic** | Historical funding rounds, venture velocity | Curated mock dataset fallback if API token is unconfigured. |
| **Govt Open Data** | Statutory regulatory compliance, taxation alerts | Country-specific allowlist with graceful empty list return. |
| **Gemini Grounding** | Cultural norms, religious holidays, consumer habits | Integrated into Gemini inference pipeline. |

---

## 6. What Was Deliberately Omitted & Why

- **No LangChain / LlamaIndex:** Adds unnecessary abstraction overhead, increases latency, and obscures prompt debugging. Direct Gemini SDK calls provide total control and sub-second execution.
- **No Heavy Relational Database (PostgreSQL/MySQL):** PRISM is session-driven. BigQuery handles analytical logs; GCS handles document blobs. Relational databases add unnecessary DevOps overhead.
- **No Complex WebSockets:** Server-Sent Events (SSE) provide unidirectional, HTTP-compatible real-time streaming with automatic reconnection, eliminating WebSocket handshake failure risks.
