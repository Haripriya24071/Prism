# PRISM 🔺
### *One idea. Six perspectives. One ground truth.*

> A multi-modal AI system that transforms raw, fragmented business ideas into production-grade, investor-ready Business Requirements Documents — stress-tested by a swarm of six expert AI agents, grounded in real-world live data, and explained line by line.

---

## What Is PRISM?

PRISM is not a document generator. It is a **structured disagreement engine**.

You drop your idea — as text, voice, image, or document — and PRISM routes it through six independent AI agents simultaneously, each operating from a radically different expert lens. These agents don't coordinate. They compete. The strongest sections from each agent are surgically merged into a single BRD that no individual agent could have produced alone.

Every requirement in the final output carries four pieces of metadata:
- **What** the requirement is
- **Which agent** produced it
- **What real-world data** supports it
- **A confidence score** backed by evidence

---

## The Team

| Name | Role |
|------|------|
| **Swapnil Ghosh** | Frontend Lead — UI architecture, animations, voice input, heatmap, BRD viewer |
| **Zahid** | Backend Lead — Swarm orchestration, Gemini API, evaluator, merge engine |
| **Haripriya** | Integrations — Context harvester APIs, BigQuery, GCS, PDF export |
| **Ritika** | QA, Testing, Documentation, Demo preparation |

---

## Core Features

- **Conversational Intake** — chat-first, zero-form UX. Voice input supported.
- **Real-Time Context Harvesting** — NewsAPI, World Bank, Crunchbase, Govt Open Data, Gemini Grounding — all fired in parallel the moment a region is detected
- **6-Agent Swarm** — VC, Lean Founder, Enterprise CTO, UX Researcher, Regulator, Adversarial Competitor — all running independently and simultaneously
- **Weighted Evaluator** — scores all 6 BRDs across 5 criteria backed by data citations
- **Merge Engine** — best base BRD + best-scoring section transplanted from each competing agent
- **Divergence Heatmap** — visual risk radar showing where agents disagreed most
- **Investor Readiness Score** — single 0–100 score with gap flags and action items
- **Failure Mode Simulation** — Agent 6 actively tries to kill your idea before you launch
- **Assumption Flagging** — every hidden assumption in the BRD surfaced and challenged
- **Pivot Suggester** — if score < 60, generates 3 concrete pivot directions with projected scores
- **Confidence Decay Monitor** — BRD freshness tracking; alerts when context has gone stale
- **Stakeholder Export Views** — same BRD, three PDFs: Investor / Technical / Regulatory

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite, Framer Motion, GSAP, Tailwind CSS |
| Voice Input | Web Speech API + Gemini Audio fallback |
| Backend | FastAPI (Python 3.11) |
| AI Core | Gemini 2.0 Flash (swarm + post-merge) + Gemini 1.5 Pro (evaluator + merge) via Vertex AI |
| Context APIs | NewsAPI, World Bank Open Data, Crunchbase Basic, Gemini Search Grounding |
| Auth & Quota | Vertex AI (google-cloud-aiplatform) — project-level quota, ADC auth |
| Storage | Google Cloud Storage |
| Analytics | BigQuery |
| PDF Export | ReportLab + Google Docs API |
| Hosting | Vercel (frontend) + Railway (backend) |

---

## Local Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Google Cloud project with Vertex AI, GCS, BigQuery enabled
- API keys: Gemini, NewsAPI, Crunchbase

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Environment Variables
See `.env.example` for the full list of required keys.

---

## Project Structure

```
prism/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBox/
│   │   │   ├── AgentGrid/
│   │   │   ├── DivergenceHeatmap/
│   │   │   ├── BRDViewer/
│   │   │   └── ScoreCard/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── styles/
│   └── public/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── intake/
│   ├── context/
│   ├── agents/
│   ├── output/
│   └── gcp/
├── .agents/
│   ├── rules/
│   └── workflows/
├── README.md
├── PRD.md
├── TECHSTACK.md
├── ARCHITECTURE.md
├── DESIGN.md
├── SCHEMA.md
├── RULES.md
└── CONTRIBUTING.md
```

---

## Hackathon

**Event:** Manipal Hackathon 2026
**Track:** Google Gemini AI + Google Cloud
**Problem Statement:** Build a scalable, multi-modal AI system using Google Gemini AI and integrated Google Cloud tools that can process real-time, fragmented data and deliver accurate, context-aware, and explainable decisions in complex and dynamic environments.

---

## License
MIT
