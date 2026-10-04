# Ritika — QA, Documentation, Pitch Deck & Demo Lead

**Role:** Quality Assurance, Pitch Deck Architect & Demo Lead  
**Owns:** 
- **Testing & Verification:** `backend/tests/`, `fixtures/`, end-to-end pipeline latency validation.
- **Environment & Spec Integrity:** `.env.example`, documentation consistency audits across PRD, Architecture, and Rules.
- **Presentation & Pitch Deck (PPT):** 6-slide executive deck, Google Cloud architecture hero slide, side-by-side comparison slide.
- **Curated Demo Scenarios & Script:** Rehearsal scripts for high-score SaaS vs. high-risk pivot ideas, fallback demo recording.

**Governing Docs:** [PRD.md](../../PRD.md), [RULES.md](../../RULES.md), [SCHEMA.md](../../SCHEMA.md), [ARCHITECTURE.md](../../ARCHITECTURE.md).

---

## 🎯 Executive Summary

Ritika established the testing foundation with high-fidelity fixtures, conducted rigorous live verification across the 12-key pool and swarm pipeline, built the official 6-slide Hackathon Pitch Deck, and scripted the live demo scenarios demonstrating PRISM's structured disagreement and pivot suggester.

---

## 📊 Completed Deliverables & Contribution Breakdown

### 1. Test Fixtures, QA & Pipeline Benchmarking

| Deliverable | Scope & Verification | Status |
| :--- | :--- | :---: |
| **Realistic JSON Fixtures** (`fixtures/`) | Built full mock fixtures for `intake_package.json`, 6 × `agent_{name}.json`, `score_matrix.json`, `merged_brd.json`, `heatmap.json`, `investor_readiness.json`, and SSE event sequences. | ✅ Complete |
| **Multi-Key Pool Verification** | Stress-tested the 12-key AI Studio pool under 6-agent concurrent execution, verifying that HTTP 429/401 triggers immediate sub-second key rotation. | ✅ Complete |
| **Heuristic Swarm Fallback QA** | Tested failure resilience by simulating upstream AI disconnects; verified Swapnil's `_generate_heuristic_brd` produces valid 6-section outputs with a 100% completion rate. | ✅ Complete |
| **End-to-End Latency Benchmarking** | Measured P95 latencies across all 10 pipeline steps: Conversational Intake (<2.5s), Context Harvest (<5.5s), 6-Agent Swarm (<18s), Rubric Evaluation (<4s), Section Merge (<3.5s), PDF Export (<2s). Total run time: **< 40 seconds**. | ✅ Complete |
| **Frontend Accessibility Audit** | Verified WCAG 2.1 AA compliance: contrast ratios on `--color-agent-*` tokens, visible focus rings, screen reader announcements on `aria-live="polite"`, and reduced-motion fallback on `HandshakeLoader.jsx`. | ✅ Complete |

---

### 2. Hackathon Pitch Deck (6 Slides)

| Slide # | Slide Title | Visual Content & Key Narrative | Status |
| :---: | :--- | :--- | :---: |
| **1** | **Title: PRISM** | Hero tagline: *"One Idea. Six Perspectives. One Ground Truth."* Features team credentials, Manipal Hackathon 2026 track, and hero product badge lineup. | ✅ Finalized |
| **2** | **The Crisis of 1-Shot AI** | Demonstrates why generic LLM prompts create "agreeable hallucinations" that collapse under enterprise scaling, regulatory scrutiny, or hacker exploitation. | ✅ Finalized |
| **3** | **The Structured Disagreement Engine** | Visual architecture showing the 6 adversarial expert personas competing simultaneously against an impartial 5-axis rubric. | ✅ Finalized |
| **4** | **Google Cloud Architecture (Hero Slide)** | Diagrams the zero-cost architecture: Gemini 2.0 Flash swarm, Google Cloud Storage hybrid persistence, BigQuery Sandbox audit analytics, and Vertex AI enterprise scale path. | ✅ Finalized |
| **5** | **Side-by-Side Visual Proof** | Compares generic 1-shot ChatGPT PRD vs. PRISM's multi-perspective BRD with lineage chips (`[LineageTag]`), live citations (`[SOURCE: worldbank]`), and divergence heatmap. | ✅ Finalized |
| **6** | **Live Metrics & Future Roadmap** | Latency benchmarks (<40s), ₹0 operational cost, and roadmap: automated sprint ticket generation and confidence decay tracking. | ✅ Finalized |

---

### 3. Curated Live Demo Scenarios & Script

| Scenario | Pitch Idea | Expected Swarm Behavior & Highlighted Features | Status |
| :--- | :--- | :--- | :---: |
| **Scenario 1: Fundable B2B SaaS** | *"Automated AI code review & security auditing for enterprise GitHub pull requests."* | Shows strong consensus between VC and CTO, high investor readiness score (**82/100, High Confidence**), minimal divergence, and deep technical architecture export. | ✅ Scripted & Rehearsed |
| **Scenario 2: High-Risk Consumer FinTech** | *"Peer-to-peer consumer lending on social media in Southeast Asia."* | Triggers severe red flags from The Regulator (statutory banking licenses) and The Adversarial (fraud rings); generates high divergence heatmap and triggers the **Strategic Pivot Suggester** with 3 actionable alternatives. | ✅ Scripted & Rehearsed |
| **Fallback Demo Video** | 75-second high-definition screen recording | Offline failsafe video recorded on desktop ready to present if venue Wi-Fi encounters drops. | ✅ Recorded & Verified |

---

## ⏱️ Live Presentation Timing Plan (3 Minutes Total)

- **0:00 – 0:35 (35s):** The Problem — Why 1-shot AI generates dangerously agreeable PRDs (Slides 1–2).
- **0:35 – 1:15 (40s):** The Solution — 6-Agent Swarm, Context Harvesting, and GCP Architecture (Slides 3–4).
- **1:15 – 2:30 (75s):** **Live System Demonstration** — Run Scenario 1 or Scenario 2 live, highlighting the HandshakeLoader, real-time agent thought bubbles, divergence heatmap, and downloadable PDF.
- **2:30 – 3:00 (30s):** Judge Q&A & Architecture Defense.
