# PRISM Backend — Antigravity Onboarding Context
### Paste this at the start of any Antigravity session to get full backend context

---

## What PRISM Does

PRISM is a multi-modal AI system that transforms a raw business idea into an investor-ready Business Requirements Document (BRD) via a 6-agent Gemini swarm.

Input: a business idea (text conversation + optional PDF/DOCX/image upload)
Output: a merged BRD with investor readiness score, heatmap, assumption flags, failure modes, optional pivot suggestions, and 3 stakeholder PDFs

---

## Tech Stack (Backend)

- **Framework:** FastAPI (Python 3.11), async throughout
- **AI:** Gemini 2.0 Flash (swarm + post-merge) + Gemini 1.5 Pro (evaluator + merge) via **Vertex AI** (google-cloud-aiplatform SDK, ADC auth — no API key rotation)
- **Storage:** Google Cloud Storage (session data + PDFs), BigQuery (run analytics)
- **Auth:** GCP service account with Application Default Credentials
- **Local dev:** GCS writes fall back to /tmp/prism-sessions/, BQ logging is skipped

---

## API Contract (for frontend — Swapnil)

Base URL: http://localhost:8000

### Flow
1. POST /intake/session → get session_id
2. POST /intake/chat (repeat) → conversation turns until is_complete: true
3. POST /intake/upload (optional) → upload PDF/DOCX/image
4. POST /generate?session_id=<id> → fires pipeline, returns stream_url
5. GET /generate/stream/<id> → SSE stream of progress events
6. GET /brd/<id> → completed BRD JSON when status == "complete"
7. GET /brd/<id>/pdf?view=investor → signed GCS URL for PDF download

### SSE Events (from /generate/stream)
Each event is a JSON object on a `data:` line:
```json
{"event": "context_ready",   "data": {"session_id": "...", "status": "complete", "progress_pct": 20}}
{"event": "agent_status",    "data": {"session_id": "...", "agent": "vc", "status": "running", "progress_pct": 35}}
{"event": "evaluation_complete", "data": {"session_id": "...", "winning_agent": "vc", "progress_pct": 80}}
{"event": "brd_ready",       "data": {"session_id": "...", "investor_score": 74, "confidence_band": "fundable", "progress_pct": 100}}
{"event": "error",           "data": {"session_id": "...", "message": "Pipeline failed", "progress_pct": 0}}
{"event": "done",            "data": {"session_id": "..."}}
```

### Response Shapes

POST /intake/session → 201
```json
{"session_id": "uuid", "status": "intake"}
```

POST /intake/chat → 200
```json
{"reply": "string", "is_complete": false, "turn": 1}
```

POST /generate → 200
```json
{"session_id": "uuid", "status": "generating", "stream_url": "/generate/stream/<id>"}
```

GET /brd/<id> → 200
```json
{
  "session_id": "uuid",
  "status": "complete",
  "investor_readiness_score": 74,
  "brd": {
    "session_id": "uuid",
    "sections": [
      {
        "title": "Executive Summary",
        "content": "...[SOURCE: worldbank]...",
        "lineage": {"source_agent": "vc", "confidence": 0.88, "data_citation": "..."}
      }
    ],
    "assumptions": [
      {"assumption": "...", "confidence": "high", "evidence": "...", "recommended_action": "..."}
    ],
    "failure_modes": [
      {"title": "...", "probability_pct": 70, "description": "...", "mitigation": "..."}
    ],
    "investor_readiness_score": 74
  }
}
```

GET /brd/<id>/pdf?view=investor → 200
```json
{"session_id": "uuid", "view": "investor", "url": "https://storage.googleapis.com/...", "available": true}
```

---

## Pipeline Steps (what happens inside /generate)

| Step | What happens | Time |
|------|-------------|------|
| 1 | Context harvest: NewsAPI + World Bank + Crunchbase + GovtData + Gemini Grounding (parallel) | ~3-8s |
| 2 | 6-agent swarm: VC, Lean Founder, CTO, UX, Regulator, Adversarial (parallel) | ~15-25s |
| 3 | Gemini Pro evaluator: scores all 6 BRDs on 5 weighted criteria | ~10-15s |
| 4 | Gemini Pro merge engine: synthesises best sections into one BRD | ~15-20s |
| 5 | Post-merge analysis: assumptions + failure modes + stakeholder reframe (parallel Flash) | ~10s |
| 6 | Pure math: heatmap std dev + investor score + gap flags | <1s |
| 7 | Pivot suggester: fires only if score < 60 | ~5s |
| 8 | PDF export: 3 stakeholder views in parallel (background) | ~5s |
| **Total** | | **~50-65s** |

Total Gemini calls per run: 14 Flash + 2 Pro = 16 calls

---

## The 6 Agent Personas

| Persona | Key Constraint | Most Likely to Surface |
|---------|---------------|----------------------|
| VC | Market > $1B TAM, 12mo Series A path | Fundability, moat, market size |
| Lean Founder | Ship in 4 weeks on $5K | Cut features, bootstrap path |
| Enterprise CTO | SOC2, 10M users, no lock-in | Security, scalability, compliance |
| UX Researcher | WCAG AA, ethnographic validation | User pain, adoption barriers |
| Regulator | GDPR/DPDP, sector licensing | Legal landmines, data residency |
| Adversarial | $10M budget to kill this product | Kill shots, competitor attacks |

---

## Scoring (for QA and slides — Ritika)

5 weighted criteria scored 0-100 per agent by Gemini Pro:
- Feasibility (25%) — viable given constraints + World Bank data
- Market Timing (20%) — aligned with NewsAPI + Crunchbase signals
- Regulatory Safety (20%) — compliant per govtdata flags
- User Adoption (20%) — adoption likelihood per cultural context
- Competitive Moat (15%) — defensibility vs competitor data

Investor Readiness Score = weighted average across all 6 agents
- 70+ = Fundable
- 50-69 = Promising
- <50 = Needs Work → Pivot Suggester fires

Heatmap = std dev of scores per criterion — high disagreement = high risk

---

## File Ownership

| Owner | Files |
|-------|-------|
| Zahid | All of backend/ |
| Swapnil | Frontend (call the API above) |
| Haripriya | GCP project setup, service account, bucket creation |
| Ritika | tests/ additions, slides, demo script |

---

## Demo Scenarios

Three pre-configured scenarios in backend/demo_config.py:
1. **IndiaFintechSMB** — IN, fintech, idea stage, $50K budget. Expected score 55-85.
2. **SingaporeEdTechB2B** — SG, edtech, MVP stage, $200K budget. Expected score 60-90.
3. **USHealthTechConsumer** — US, healthtech, prototype stage, $150K budget. Expected score 50-80.

Run: `python backend/demo_runner.py IndiaFintechSMB`
