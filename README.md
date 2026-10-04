# PRISM 🔺
### *One Idea. Six Perspectives. One Ground Truth.*

> **A multi-modal AI intelligence engine that transforms raw, fragmented startup ideas into institutional-grade, investor-ready Business Requirements Documents — stress-tested by a swarm of 6 competing AI agents, grounded in real-time market data, and explained line by line.**

---

## 🌟 What Is PRISM?

PRISM is not a template generator. It is a **Structured Disagreement Engine**.

Traditional AI tools generate agreeable, single-shot PRDs that collapse when exposed to technical scale, regulatory scrutiny, or market competition. PRISM routes your business idea simultaneously through six independent expert personas operating from adversarial mandates:

1. 💜 **The VC:** Demands 10x scalability, TAM expansion, and defensible moats.
2. 🩵 **The Lean Founder:** Ruthlessly cuts scope to force a 4-week validation MVP.
3. 💚 **The Enterprise CTO:** Audits system architecture, security, and infrastructure costs.
4. 🧡 **The UX Researcher:** Champions user psychology, onboarding friction, and habit loops.
5. 💙 **The Regulator:** Audits data privacy (GDPR/DPDP), statutory filings, and legal liabilities.
6. ❤️ **The Adversarial Competitor:** Actively attempts to kill your business model and exploit weaknesses.

PRISM records their debate, evaluates all contributions against a 5-axis rubric, transplants the strongest sections into a unified BRD with full lineage attribution, and maps disagreement into a **Visual Divergence Heatmap**.

---

## 🏆 Hackathon Alignment

- **Event:** Manipal Hackathon 2026
- **Track:** Google Gemini AI + Google Cloud Tools
- **Challenge:** *Build a scalable, multi-modal AI system using Google Gemini AI and integrated Google Cloud tools (such as Vertex AI, Cloud Storage, and BigQuery) that can process real-time, fragmented data (text, images, and documents) and deliver accurate, context-aware, and explainable decisions in complex and dynamic environments.*

### How PRISM Delivers for ₹0:
- **Google Gemini 2.0 Flash:** High-throughput 12-key pool supporting up to 180+ RPM without rate limits or inference costs.
- **Multi-Modal Data Intake:** Ingests unformatted text, speech (Web Speech API), images/wireframes (Gemini Vision), and pitch decks (PyPDF2/python-docx).
- **Google Cloud Storage:** Stores all session JSON files and compiled PDFs following production GCS prefix hierarchy with local hybrid fallback in development.
- **Google BigQuery:** Live dataset `prism_data` with `brd_runs` and `context_harvest_logs` tables in BigQuery Sandbox for decision auditability.
- **Vertex AI:** Enterprise production architecture ready for direct ADC integration.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Node.js:** v18.x or v20.x
- **Python:** v3.11+ (Python 3.11, 3.12, 3.13 or 3.14)
- **Virtual Environment:** `.venv`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173
```

### 3. Backend Setup
```bash
# In the project root:
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

# Run FastAPI backend:
uvicorn backend.main:app --reload --port 8000
# API Docs available at: http://localhost:8000/docs
```

---

## ⚙️ Environment Variables

Create a `backend/.env` file with your credentials:

```env
# ── Gemini Multi-Key Pool (100% Free Forever) ──
GEMINI_API_KEY_1=your_ai_studio_key_here
GEMINI_API_KEY_2=your_second_key_here
GEMINI_FLASH_MODEL=gemini-flash-latest
GEMINI_PRO_MODEL=gemini-flash-latest

# ── Google Cloud Architecture Configuration ──
GCP_PROJECT_ID=prism-hackathon-510523
GCP_REGION=us-central1
GCS_BUCKET_NAME=prism-outputs
BIGQUERY_DATASET=prism_data
GOOGLE_APPLICATION_CREDENTIALS=./prism-hackathon-key.json

# ── Server Settings ──
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENV=development
```

---

## 👥 The Team

| Name | Role | Responsibilities |
| :--- | :--- | :--- |
| **Swapnil Ghosh** | Frontend Lead & Prompts | React 18 UI, design system, animations, SSE streaming, persona system prompts |
| **Zahid** | Backend Core & Pipeline | FastAPI orchestrator, Gemini multi-key pool, 6-agent swarm, evaluation rubric |
| **Haripriya** | Integrations & GCP Storage | Context harvester APIs, BigQuery tables, Cloud Storage persistence, PDF export |
| **Ritika** | QA, Docs & Demo | Test fixtures, pitch deck (PPT), demo rehearsal, fallback video recording |

---

## 📄 License
MIT License. Built for Manipal Hackathon 2026.
