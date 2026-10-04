# Haripriya — Integrations, Cloud Storage, BigQuery & Output

**Owns:** `backend/context/`, `backend/gcp/`, `backend/output/assumptions.py`, `failure_sim.py`, `pdf_export.py`, `stakeholder.py`.  
**Does not touch:** `backend/models/` (Zahid owns), `backend/main.py`, `frontend/`.  
**Governing docs:** [ARCHITECTURE.md](../../ARCHITECTURE.md), [SCHEMA.md](../../SCHEMA.md), [RULES.md](../../RULES.md) (ARCH-010, SEC-003/004/006/007, DB-001 to DB-015).

---

## Current Status Overview
- **Phase 0 (Setup & Contracts):** ✅ 100% Complete. Service account created, BigQuery dataset `prism_data` and tables `brd_runs` & `context_harvest_logs` provisioned in BigQuery Sandbox.
- **Phase 1 (Context Harvesters):** ✅ 90% Complete. Clients for NewsAPI, World Bank, Crunchbase, Govt Data, and Gemini Grounding structured with graceful fallbacks.
- **Phase 2 (Harvester & Storage):** ✅ 100% Complete. Hybrid GCS persistence (`backend/gcp/storage.py`) writes JSON/PDF following exact GCS folder structure; BigQuery logging helpers implemented.
- **Phase 3 (Output Layer & PDF Export):** 🟡 80% Complete. Assumption flagging, failure simulation, stakeholder view reframing implemented; ReportLab PDF export verification on deck.

---

## Phase 0 — Cloud Setup & Contracts (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 0.1 | Obtain and configure GCP project & service account credentials | Service account created with key `prism-hackathon-510523-489baa57ba00.json`. | ✅ Done |
| 0.2 | Model sign-off with Zahid | `ContextPackage`, `NewsItem`, `MarketData` aligned to Pydantic models. | ✅ Done |
| 0.3 | **BigQuery Dataset (`prism_data`)** | Created in BigQuery Sandbox (10GB storage + 1TB query/mo 100% free, 0 card needed). | ✅ Done |
| 0.4 | **BigQuery Tables Provisioned** | `prism_data.brd_runs` and `prism_data.context_harvest_logs` created with schema. | ✅ Done |

---

## Phase 1 — Context Harvester Clients (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 1.1 | `context/newsapi.py` | Fetches real-time industry/regional news with in-memory caching. | ✅ Done |
| 1.2 | `context/worldbank.py` | Extracts GDP per capita, ease of doing business, inflation, FDI. | ✅ Done |
| 1.3 | `context/govtdata.py` | Regional regulatory alerts and statutory flags (graceful empty list fallback). | ✅ Done |
| 1.4 | `context/crunchbase.py` | Market funding activity with static mock fallback if key is unconfigured. | ✅ Done |
| 1.5 | `context/grounding.py` | Gemini search grounding for cultural nuances, seasonal timing, and user behavior. | ✅ Done |
| 1.6 | Region and industry input sanitization | Prevents injection and handles missing values cleanly. | ✅ Done |

---

## Phase 2 — Harvester Orchestration & Storage Persistence (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 2.1 | **`backend/gcp/storage.py` (Hybrid Cloud Storage)** | Writes session JSON files with `content_type="application/json"`. In production, uploads to GCS bucket; in development/demo, saves to `/tmp/prism-sessions/{session_id}/` maintaining the exact GCS folder hierarchy. Never crashes. | ✅ Done |
| 2.2 | `context/harvester.py` | Runs all 5 context sources in parallel via `asyncio.gather(..., return_exceptions=True)`. Assembles `ContextPackage` in < 8s. | ✅ Done |
| 2.3 | **`backend/gcp/bigquery.py` (Audit Logging)** | Fire-and-forget logging to `brd_runs` and `context_harvest_logs`. Runs in background without blocking API response. | ✅ Done |
| 2.4 | Parallel read helpers | Reads all 6 agent outputs simultaneously for the merge engine. | ✅ Done |

---

## Phase 3 — Output Analysis & PDF Generation (Active)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 3.1 | `backend/output/assumptions.py` | Scans merged BRD for unstated assumptions with confidence ratings and validation actions. | ✅ Done |
| 3.2 | `backend/output/failure_sim.py` | Extracts Agent 6 adversarial analysis into top 3 failure modes with probability, description, and mitigation. | ✅ Done |
| 3.3 | `backend/output/stakeholder.py` | Generates 3 customized orderings of the BRD: Investor view, Technical view, Regulatory view. | ✅ Done |
| 3.4 | **`backend/output/pdf_export.py` (ReportLab)** | Generates clean, professional PDF documents for all 3 views (`output_investor.pdf`, `output_technical.pdf`, `output_regulatory.pdf`). Executed via `asyncio.to_thread` (ARCH-010). | 🔄 Active Verification |
| 3.5 | `GET /brd/{id}/pdf?view=` endpoint support | Serves generated PDF stream directly to Swapnil's UI download button. | 🟡 Hooked |

**Exit Criteria:** ReportLab PDF generates in < 3s, visually inspected, lineage and data citation tags rendered cleanly.

---

## Phase 4 — Resilience & Demo Polish (Final Milestone)

- Test harvester with individual sources disabled to confirm zero pipeline crashes.
- Verify no credentials or API keys appear in application logs (SEC-006).
- Confirm BigQuery sandbox logging operates silently in the background.
- Freeze code for team demo rehearsals.
