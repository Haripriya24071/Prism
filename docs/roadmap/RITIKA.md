# Ritika — QA, Documentation, Pitch Deck & Demo Lead

**Owns:** `backend/tests/`, `fixtures/`, `.env.example`, documentation review, Hackathon Pitch Deck (PPT), demo script, fallback demo recording.  
**Does not touch:** application code directly. Reports bugs to module owners with reproductions.  
**Governing docs:** [PRD.md](../../PRD.md), [RULES.md](../../RULES.md), [SCHEMA.md](../../SCHEMA.md), [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## Current Status Overview
- **Phase 0 (Fixtures & Test Setup):** ✅ 100% Complete. Fixtures and mock schemas aligned to Pydantic models.
- **Phase 1 (Module Testing):** ✅ 90% Complete. Verified intake, key rotation, and swarm execution live.
- **Phase 2 (Core Pipeline Verification):** ✅ 90% Complete. Live test executed: 12-key pool rotating with zero crashes; 5/5 active agents completed full 6-section BRDs.
- **Phase 3 (Integration & QA):** 🟡 Active. Verifying end-to-end flow from frontend (`localhost:5173`) to backend (`localhost:8000`).
- **Phase 4 & 5 (Pitch Deck & Demo Rehearsal):** 🚀 **CRITICAL PATH RIGHT NOW.**

---

## Phase 0 — Fixtures and Test Foundation (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 0.1 | `fixtures/`: Realistic JSON fixtures | Intake package, 6 agent outputs, score matrix, merged BRD, divergence heatmap, investor readiness. | ✅ Done |
| 0.2 | SSE fixture: Event sequence matching ARCHITECTURE.md | Replayable event stream for UI testing. | ✅ Done |
| 0.3 | Pytest setup: `backend/tests/` | Test structure and configuration. | ✅ Done |
| 0.4 | `.env.example` maintenance | Documenting all 20 Gemini key pool slots and GCP project parameters. | ✅ Done |
| 0.5 | Documentation consistency check | Aligned model names, architecture diagrams, and persistence layers across docs. | ✅ Done |

---

## Phase 1 & 2 — Pipeline QA & Live Verification (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 1.1 | Gemini Key Pool Verification | Tested all 13 keys; validated 12 active keys; confirmed automatic failover on 401/429. | ✅ Done |
| 1.2 | Swarm Execution QA | Verified 6 agents running in parallel; confirmed partial failure resilience (≥4 of 6 proceed). | ✅ Done |
| 1.3 | JSON Parsing Reliability | Verified regex fence cleaner parses structured JSON even when wrapped in commentary. | ✅ Done |
| 1.4 | GCS & BigQuery Fallback QA | Confirmed storage saves files to `/tmp/prism-sessions/` adhering strictly to the GCS URI structure. | ✅ Done |

---

## Phase 3 — Integration QA & Performance Verification (Active)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 3.1 | End-to-end latency validation | Ensure total run from idea submission to scorecard is < 50s P95. | 🔄 Active |
| 3.2 | Frontend accessibility & UX check | Verify focus rings, keyboard navigation, and reduced-motion compliance. | 🔄 Active |
| 3.3 | Error resilience audit | Test behavior when an invalid file is uploaded or when network latency occurs. | 🔄 Active |

---

## Phase 4 — Pitch Deck (PPT) & Demo Script (Top Priority)

| # | Deliverable | Detailed Description | Status |
|---|-------------|----------------------|--------|
| 4.1 | **Pitch Deck Structure (6 Slides)** | 1. **Title:** PRISM — Multi-Modal Disagreement Engine<br>2. **The Problem:** Single-shot LLM prompts generate generic, unchallenged PRDs that fail in production.<br>3. **The Solution:** 6 adversarial expert AI agents competing simultaneously, grounded in live market intelligence.<br>4. **Google Cloud Architecture (Hero Slide):** Show Gemini 2.0 Flash swarm, Cloud Storage multimodal persistence, BigQuery decision audit analytics, and Vertex AI enterprise scale path.<br>5. **Competitive Edge / Live Metrics:** Lineage attribution, divergence heatmap, and instant investor readiness scoring.<br>6. **Future Roadmap:** Confidence decay tracking and automated sprint planning. | 🔄 Active |
| 4.2 | **Side-by-Side Comparison Slide** | Real visual comparison: Generic 1-shot ChatGPT output vs. PRISM's multi-perspective BRD with data citations and risk heatmap. | 🔄 Active |
| 4.3 | **Demo Script (2 Curated Ideas)** | - **Idea 1 (Fundable B2B SaaS):** "Automated AI code review & security auditing for GitHub pull requests" &rarr; demonstrates high score, multi-agent consensus, and deep technical architecture.<br>- **Idea 2 (High-Risk Pivot):** "Peer-to-peer consumer lending on social media in Southeast Asia" &rarr; triggers Regulator & Adversarial red flags, high heatmap divergence, and the Pivot Suggester. | 🔄 Active |
| 4.4 | **Fallback Demo Video** | Record a 60–90 second clean walkthrough of the working UI as an offline failsafe. | 🔄 Active |

---

## Phase 5 — Team Rehearsal & Final Freeze

- Run two full rehearsals with Swapnil, Zahid, and Haripriya.
- Time the live presentation to exactly **2 minutes 30 seconds** (leaving 30s for judge Q&A).
- Verify clean clone instructions in `README.md`.
- Enforce feature freeze — zero new code changes after rehearsals.

**Exit Criteria:** Flawless live demo execution, slides finalized, backup video ready on desktop.
