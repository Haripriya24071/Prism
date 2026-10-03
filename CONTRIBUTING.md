# PRISM — Contributing Guide

---

## Team

| Name | GitHub Handle | Area |
|------|--------------|------|
| Swapnil Ghosh | @swapnil | Frontend Lead |
| Zahid | @zahid | Backend Lead |
| Haripriya | @haripriya | Integrations |
| Ritika | @ritika | QA + Docs + Demo |

---

## Work Division

Phased plans with deliverables and exit criteria live in `docs/roadmap/`: [SWAPNIL](docs/roadmap/SWAPNIL.md), [ZAHID](docs/roadmap/ZAHID.md), [HARIPRIYA](docs/roadmap/HARIPRIYA.md), [RITIKA](docs/roadmap/RITIKA.md).

### Swapnil — Frontend
- Overall UI architecture and component structure
- Conversational ChatBox (text + voice input)
- AgentGrid with live SSE status updates
- Divergence Heatmap (GSAP animations)
- BRD Viewer with lineage tags and assumption flags
- ScoreCard with animated ring (GSAP count-up)
- Stakeholder export view selector
- Framer Motion page transitions
- Design token system (CSS custom properties)
- Responsive layout (3 breakpoints)
- Swarm persona definitions and system prompts (`agents/personas.py`, `agents/prompts.py`)

### Zahid — Backend
- FastAPI application, route structure, `config.py`, `errors.py`, log sanitiser
- Pydantic models for all request/response shapes
- Intake processor (conversation, Vision, document parser, extractor)
- Swarm orchestration (`asyncio.gather` — 6 parallel Flash calls)
- Gemini API key rotation logic (pool of 20 keys)
- Evaluator (Gemini Pro — weighted rubric scoring)
- Merge Engine (Gemini Pro — best section transplanting)
- Heatmap and investor score calculation, Pivot Suggester (stretch)
- SSE streaming endpoint (`/generate/stream/{session_id}`)
- Vertex AI job tracking

### Haripriya — Integrations + Output
- Context Harvester (all 5 external APIs)
  - NewsAPI integration
  - World Bank Open Data integration
  - Crunchbase Basic integration
  - Govt Open Data integration
  - Gemini Search Grounding
- GCS read/write (`backend/gcp/storage.py`)
- BigQuery logging (`backend/gcp/bigquery.py`)
- Assumption flagging and failure mode simulation
- PDF export (ReportLab — 3 stakeholder views)

### Ritika — QA + Demo
- Mock fixtures for frontend development (`fixtures/`)
- Test coverage for all backend modules (pytest)
- Frontend integration testing
- Demo script and walkthrough preparation
- `.env.example` maintained and documented
- PPT slides — design and content
- Demo video recording
- README and documentation review

---

## Development Setup

### Prerequisites
- **Google Antigravity 2.0** — download free from `antigravity.google/download` (macOS / Windows / Linux)
- Google account (for Antigravity sign-in + GCP access)
- Google Cloud project (Vertex AI + GCS + BigQuery enabled)
- Gemini API keys (minimum 1, ideally 20 for full pool)
- NewsAPI key
- Crunchbase Basic key

### Clone and Setup

```bash
# 1. Sign into Antigravity
antigravity auth login   # uses your Google account

# 2. Clone and open in Antigravity IDE
git clone https://github.com/your-org/prism.git
cd prism
antigravity .

# 3. Connect GCP project inside Antigravity
# Settings → Cloud → Connect Project → select your GCP project
# GCS, BigQuery, Vertex AI are auto-configured — no manual credential wiring
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
# Fill in VITE_API_BASE_URL=http://localhost:8000
npm run dev
# Antigravity auto-detects the Vite dev server and opens a live preview
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in all API keys (see Environment Variables section below)
uvicorn main:app --reload --port 8000
```

---

## Git Workflow

### Single Branch: `main`
All work goes to `main`. No feature branches, no PRs.

1. `git pull --rebase origin main` before starting work and before every push
2. Edit only files in your own area (see Work Division and `docs/roadmap/`)
3. Need a change in someone else's file? Ask the owner; do not edit it yourself
4. Run the local checks below. Never push code that fails them
5. Commit small, one logical change each. Push often
6. Never force-push to `main`

### Commit Format
```
type(scope): short description

Types: feat | fix | refactor | test | docs | style | chore
Scopes: frontend | backend | swarm | context | intake | output | gcp | docs

Examples:
feat(swarm): add API key rotation logic
fix(context): handle NewsAPI timeout gracefully
feat(frontend): add GSAP heatmap bar animation
docs(readme): update setup instructions
```


---

## Local Checks

**Backend:**
```bash
cd backend
mypy .                          # type checking
pytest tests/ -v                # run all tests
python -c "import main"         # verify no circular imports
```

**Frontend:**
```bash
cd frontend
npm run lint                    # eslint
npm run build                   # verify production build
```

---

## Environment Variables

All keys documented in `.env.example`. Never commit `.env` or `.env.local`.

**Backend `.env`:**
```
# Gemini API Keys (pool of up to 20)
GEMINI_KEY_1=
GEMINI_KEY_2=
# ... up to GEMINI_KEY_20

# Model names (do not change without updating TECHSTACK.md)
GEMINI_FLASH_MODEL=gemini-1.5-flash
GEMINI_PRO_MODEL=gemini-1.5-pro

# Google Cloud
GCP_PROJECT_ID=
GCS_BUCKET_NAME=prism-outputs
BIGQUERY_DATASET=prism_data

# External APIs
NEWSAPI_KEY=
CRUNCHBASE_KEY=

# App
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

**Frontend `.env.local`:**
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Folder Structure

```
prism/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBox/
│   │   │   │   ├── ChatBox.jsx
│   │   │   │   ├── VoiceButton.jsx
│   │   │   │   └── ChatBox.css
│   │   │   ├── AgentGrid/
│   │   │   │   ├── AgentGrid.jsx
│   │   │   │   ├── AgentCard.jsx
│   │   │   │   └── AgentGrid.css
│   │   │   ├── DivergenceHeatmap/
│   │   │   │   ├── DivergenceHeatmap.jsx
│   │   │   │   └── DivergenceHeatmap.css
│   │   │   ├── BRDViewer/
│   │   │   │   ├── BRDViewer.jsx
│   │   │   │   ├── BRDSection.jsx
│   │   │   │   ├── LineageTag.jsx
│   │   │   │   ├── AssumptionFlag.jsx
│   │   │   │   └── BRDViewer.css
│   │   │   └── ScoreCard/
│   │   │       ├── ScoreCard.jsx
│   │   │       ├── ScoreRing.jsx
│   │   │       └── ScoreCard.css
│   │   ├── hooks/
│   │   │   ├── useSSE.js          (SSE connection + cleanup)
│   │   │   ├── useVoiceInput.js   (Web Speech API)
│   │   │   └── useSession.js      (session state management)
│   │   ├── pages/
│   │   │   ├── IntakePage.jsx
│   │   │   ├── GenerationPage.jsx
│   │   │   └── ResultsPage.jsx
│   │   ├── styles/
│   │   │   └── tokens.css         (all CSS custom properties)
│   │   └── main.jsx
│   ├── public/
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── errors.py
│   ├── models/
│   │   ├── intake.py
│   │   ├── context.py
│   │   ├── agents.py
│   │   ├── brd.py
│   │   └── output.py
│   ├── intake/
│   │   ├── conversation.py
│   │   ├── vision.py
│   │   ├── document.py
│   │   └── extractor.py
│   ├── context/
│   │   ├── harvester.py
│   │   ├── newsapi.py
│   │   ├── worldbank.py
│   │   ├── crunchbase.py
│   │   ├── govtdata.py
│   │   └── grounding.py
│   ├── agents/
│   │   ├── swarm.py
│   │   ├── prompts.py
│   │   └── personas.py
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   ├── rubric.py
│   │   └── merger.py
│   ├── output/
│   │   ├── heatmap.py
│   │   ├── investor_score.py
│   │   ├── pivot.py
│   │   ├── assumptions.py
│   │   ├── failure_sim.py
│   │   ├── pdf_export.py
│   │   └── stakeholder.py
│   ├── gcp/
│   │   ├── storage.py
│   │   └── bigquery.py
│   ├── middleware/
│   │   └── log_sanitizer.py
│   ├── tests/
│   │   ├── test_intake.py
│   │   ├── test_context.py
│   │   ├── test_swarm.py
│   │   ├── test_evaluator.py
│   │   └── test_output.py
│   └── requirements.txt
│
├── .agents/
│   └── rules/
│       ├── architecture.md
│       ├── ui-ux.md
│       ├── database.md
│       └── security.md
│
├── README.md
├── PRD.md
├── TECHSTACK.md
├── ARCHITECTURE.md
├── DESIGN.md
├── SCHEMA.md
├── RULES.md
└── CONTRIBUTING.md
```
