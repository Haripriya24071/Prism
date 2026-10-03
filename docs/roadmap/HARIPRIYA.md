# Haripriya — Integrations, Storage and Output

**Owns:** `backend/context/`, `backend/gcp/`, `backend/output/assumptions.py`, `failure_sim.py`, `pdf_export.py`, `stakeholder.py`
**Does not touch:** `models/` (Zahid owns it. Request changes), `main.py`, `frontend/`.
**Governing docs:** [ARCHITECTURE.md](../../ARCHITECTURE.md), [SCHEMA.md](../../SCHEMA.md), [RULES.md](../../RULES.md) (ARCH-010, SEC-003/004/006/007, DB-001 to DB-015)

Phases are gated by exit criteria, not dates.

---

## Phase 0 — Setup and Contract Review

| # | Deliverable | Notes |
|---|-------------|-------|
| 0.1 | Obtain and test all keys: NewsAPI, Crunchbase Basic, GCP project with GCS, BigQuery, Vertex enabled | **confirm Crunchbase access now.** If the free tier gives no usable API, switch to the fallback in 1.4 |
| 0.2 | Review Zahid's `ContextPackage`, `NewsItem`, `MarketData` models. Confirm they fit what each API actually returns | sign-off gate |
| 0.3 | Create bucket `prism-outputs` with uniform bucket-level access and dataset `prism_data` | names from `config.py` only |
| 0.4 | Create four BigQuery tables per SCHEMA.md with partitioning and clustering | document the DDL in `gcp/` as a comment-free `.sql` file or script |

**Exit:** every key works from a scratch script. Models signed off. Bucket and tables exist.

---

## Phase 1 — Context Harvester Clients

Each client: `httpx.AsyncClient`, timeout from config, returns a typed model, never raises on a bad response, never logs keys.

| # | Deliverable | Notes |
|---|-------------|-------|
| 1.1 | `context/newsapi.py` | 100 requests/day. Add a small in-process cache keyed on region + industry |
| 1.2 | `context/worldbank.py`: GDP, ease of business rank, inflation, FDI | check each indicator still exists. Handle missing years |
| 1.3 | `context/govtdata.py` | open data is country-specific. Start with India and one fallback. Return an empty regulatory list, not an error, for unsupported regions |
| 1.4 | `context/crunchbase.py` | if API access is unavailable, build a clearly labelled static-data fallback and mark `cached=true` in logs. Be honest about this in the demo |
| 1.5 | `context/grounding.py`: Gemini Search Grounding for cultural layer | uses Zahid's Gemini client wrapper |
| 1.6 | Input sanitising on region and industry before every call (SEC-003, SEC-004) | even though intake already sanitises |

**Exit:** each client has a passing test (mocked HTTP) and a manual live call. Failure and timeout return a typed empty result.

---

## Phase 2 — Harvester and Storage

| # | Deliverable | Notes |
|---|-------------|-------|
| 2.1 | `gcp/storage.py`: write JSON with `content_type="application/json"`, confirm the write, check existence before read, lowercase session ID in path. Paths from session ID only | DB-001, 002, 004, 005, 015. **Zahid needs this at the start of his Phase 2** |
| 2.2 | Parallel read helper for all six agent blobs (`asyncio.gather`) | DB-010 |
| 2.3 | `context/harvester.py`: `asyncio.gather(..., return_exceptions=True)` over the five sources, assembles `ContextPackage`, records which sources succeeded | DB-011. Emits data for the `context_ready` SSE event |
| 2.4 | `gcp/bigquery.py`: `insert_rows_json`, fire-and-forget via `create_task`, errors logged at WARNING, table names from config | DB-006 to DB-009. Never on the hot path |
| 2.5 | Harvest logging: one row per source call into `context_harvest_logs` | |

**Exit:** a region and industry produce a `ContextPackage` in under 8s P95 with one source deliberately failing. Rows appear in BigQuery. Storage rejects traversal-style input.

---

## Phase 3 — Output Layer

| # | Deliverable | Notes |
|---|-------------|-------|
| 3.1 | `output/assumptions.py`: scan merged BRD for hidden assumptions, each with confidence, evidence, action | input is a `MergedBRD`, output appends to it |
| 3.2 | `output/failure_sim.py`: Agent 6 output to top 3 failure modes with probability, description, mitigation, grounded in harvested data | |
| 3.3 | `output/stakeholder.py`: one Gemini call produces investor, technical and regulatory orderings of the same BRD | |
| 3.4 | `output/pdf_export.py`: ReportLab, three PDFs, written to `output_{view}.pdf` | CPU-bound. Use `asyncio.to_thread` (ARCH-010) |
| 3.5 | PDF design: readable typography, section headers, lineage tags and citations shown per section. Plain and clean, not decorative | |
| 3.6 | Expose `GET /brd/{id}/pdf?view=` through Zahid's routes | he adds the route, you provide the service function |

**Exit:** three PDFs generated from a real merged BRD in under 3s. Opened and visually checked. Lineage and citations are present.

---

## Phase 4 — Integration and Resilience

- Run the harvester with each source disabled in turn. The pipeline must still finish
- Verify no key ever appears in logs (SEC-006)
- Confirm BigQuery failure never slows a run
- Check free-tier consumption. NewsAPI at 100 requests per day will run out during rehearsal, so the cache must work

**Exit:** five concurrent sessions complete without storage or quota errors.

---

## Phase 5 — Freeze

- Pre-warm the cache for the demo ideas and regions
- Verify bucket permissions on the deployed environment
- Bug fixes only

---

## Dependencies

| Need | From | By |
|------|------|----|
| `ContextPackage` and related models | Zahid | end of Phase 0 |
| Gemini client wrapper | Zahid | Phase 1 (for grounding) |
| Merged BRD and agent output shapes | Zahid | Phase 3 |
| Fixtures to test against | Ritika | continuous |

## Risks

- **Crunchbase.** The free API may not exist in a usable form. Decide in Phase 0.
- **NewsAPI quota.** 100 requests per day is easy to burn. Cache aggressively.
- **Govt data.** There is no uniform source. Scope to the demo regions only.
- **Storage is on the critical path.** Zahid's swarm cannot persist without `gcp/storage.py`. Deliver 2.1 first.
