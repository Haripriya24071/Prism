# PRISM — Tech Stack

> Everything is free tier. Everything is justified. Nothing is here for show.

---

## Frontend

| Technology | Version | Why |
| --- | --- | --- |
| React | 18.x | Component model fits our multi-panel UI (chat, agent grid, heatmap, BRD viewer) |
| Vite | 5.x | Fast HMR in Antigravity, zero config |
| Framer Motion | 11.x | Declarative animations for agent card state transitions, BRD section reveals |
| GSAP | 3.x | Timeline-based animations for the divergence heatmap bars and score ring |
| Tailwind CSS | 3.x | Utility-first, pairs cleanly with our CSS token system |
| Web Speech API | Native | Voice intake — zero dependency, built into Chrome/Edge |

### Frontend Rules

- No hardcoded hex values — all colours via CSS custom property tokens
- All animations use `transform` + `opacity` only — no layout-triggering properties
- Canvas animations use `requestAnimationFrame` exclusively
- `prefers-reduced-motion` respected on all animations
- No barrel index files — explicit imports only
- React components: default exports. Utilities: named exports.

---

## Backend

| Technology | Version | Why |
| --- | --- | --- |
| Python | 3.11 | asyncio support, typing, Pydantic v2 |
| FastAPI | 0.111.x | Async-native, Pydantic integration, SSE support |
| Pydantic v2 | 2.x | Request/response validation on every endpoint |
| httpx | 0.27.x | Async HTTP client for external API calls |
| uvicorn | 0.29.x | ASGI server |
| python-magic | 0.4.x | MIME type validation on file uploads |
| ReportLab | 4.x | PDF generation for BRD export |
| PyPDF2 | 3.x | Extracting text from uploaded PDFs |
| python-docx | 1.x | Extracting text from uploaded Word docs |

### Backend Rules

- All route handlers are thin — max 30 lines, one service call
- No synchronous blocking calls inside `async def`
- All config values from `config.py` — no hardcoded strings anywhere
- Pydantic models on every request and response shape
- SSE connections cleaned up on component unmount

---

## AI Layer

| Model | Usage | Tier |
| --- | --- | --- |
| Gemini 2.0 Flash | Swarm (6 calls) + Intake (1 call) + Post-merge (3 calls) via Vertex AI | Vertex AI Quota |
| Gemini 1.5 Pro | Evaluator + Merge Engine (2 calls) via Vertex AI | Vertex AI Quota |
| Gemini Vision | Image context extraction during intake | Vertex AI (via Flash) |
| Gemini Audio | Voice input fallback (when Web Speech API unavailable) | Vertex AI |
| Gemini Search Grounding | Cultural + regulatory context harvesting | Free (within Gemini API) |

### Authentication & Quota

- Vertex AI (google-cloud-aiplatform SDK) — project-level quota, no per-key rotation
- Single GCP service account with Application Default Credentials (ADC)

---

## Context Harvester APIs

| API | Data Provided | Free Tier |
| --- | --- | --- |
| NewsAPI | Political climate, domain news, recent events | 100 requests/day |
| World Bank Open Data | GDP, ease of doing business, inflation, FDI | Unlimited (fully open) |
| Crunchbase Basic | Competitor funding rounds, market activity | Limited free tier |
| Govt Open Data Portals | Region-specific regulatory flags | Open (country-specific) |
| Gemini Search Grounding | Cultural nuances, social sensitivities, seasonal patterns | Free within Gemini API |

All 5 sources called in parallel via `asyncio.gather()` with `return_exceptions=True`. A single slow API never blocks the others.

---

## Google Cloud Platform

| Service | Usage | Free Tier |
| --- | --- | --- |
| Vertex AI | Swarm job orchestration, agent state tracking | $300 free credits |
| Cloud Storage (GCS) | Agent output blobs, merged BRD, PDF output | 5 GB free |
| BigQuery | Context harvest logs, BRD run metadata, evaluator scores | 10 GB storage + 1 TB queries/month free |
| Google Docs API | Optional BRD export as Google Doc | Free |

### GCS Blob Structure

```text
prism-outputs/{session_id}/
├── intake_package.json
├── agent_vc.json
├── agent_lean.json
├── agent_cto.json
├── agent_ux.json
├── agent_regulator.json
├── agent_adversarial.json
├── score_matrix.json
├── merged_brd.json
├── heatmap.json
├── investor_readiness.json
├── output_investor.pdf
├── output_technical.pdf
└── output_regulatory.pdf
```

---

## Infrastructure & Hosting

| Service | What | Free Tier |
| --- | --- | --- |
| Vercel | Frontend hosting | Free |
| Railway | FastAPI backend | Free tier (500 hrs/month) |
| Google Antigravity 2.0 | Development environment | Free (public preview) |

---

## Development Environment

**Google Antigravity 2.0** — all development happens here.

Download: `antigravity.google/download` — free during public preview, available on macOS, Windows, and Linux.

Antigravity 2.0 gives us:

- VS Code-based AI IDE (Editor View) with full terminal
- Agent Manager surface — higher-level task orchestration across the whole codebase
- Native Google Cloud project integration — GCS, BigQuery, Vertex AI all connect directly
- Built-in browser access for live testing
- Supports Gemini 2.0 Flash natively (our primary model) + Claude Sonnet 4.6 as fallback
- Antigravity CLI for terminal-first workflows (`antigravity` command)
- Fractal Memory system — persistent context across sessions

### Why Antigravity Over Cursor / Windsurf / IDX

- Native GCP integration means no manual credential wiring for GCS, BigQuery, Vertex AI
- Agent Manager lets us delegate whole modules (e.g. "build the context harvester") not just autocomplete lines
- Free during preview — no subscription cost on top of our already-free stack
- Gemini 2.0 Flash is the same model we're calling in our swarm — consistent behaviour

### Workspace Setup

```bash
# Install Antigravity CLI
# Download from antigravity.google/download and install for your OS

# Sign in
antigravity auth login   # uses your Google account

# Clone and open PRISM
git clone https://github.com/your-org/prism.git
cd prism
antigravity .            # opens in Antigravity IDE

# Connect to Google Cloud project
# Settings → Cloud → Connect Project → select your GCP project
# GCS, BigQuery, Vertex AI auto-configured from here
```

### Recommended Antigravity Extensions

```text
ms-python.python
esbenp.prettier-vscode
bradlc.vscode-tailwindcss
ms-python.mypy-type-checker
```

---

## What We Deliberately Did Not Use

| Skipped | Reason |
| --- | --- |
| LangChain / LlamaIndex | Unnecessary abstraction over direct Gemini API calls — adds latency and obscures control flow |
| Redux | Overkill for our state shape — React Context + local state is sufficient |
| Docker | Antigravity + Railway handle environment — adds setup time with no demo benefit |
| PostgreSQL | No relational data — GCS blobs + BigQuery covers all persistence needs |
| WebSockets | SSE is sufficient for one-directional agent status streaming |
