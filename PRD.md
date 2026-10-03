# PRISM — Product Requirements Document
**Version:** 1.0 | **Team:** Swapnil, Zahid, Haripriya, Ritika | **Date:** October 2026
**Hackathon:** Manipal Hackathon 2026 | **Track:** Google Gemini AI + Google Cloud

---

## 1. Executive Summary

PRISM is a multi-modal AI system that transforms raw, unstructured business ideas — expressed as text, voice, images, or documents — into production-grade Business Requirements Documents (BRDs) backed by live market intelligence.

PRISM is not a document generator. It is a **structured disagreement engine**.

It routes a business idea through six independent AI agents simultaneously — each with a radically different expert persona — then evaluates, merges, and presents the synthesised output with full lineage attribution, confidence scoring, and real-world data grounding.

**Core thesis:** A single AI call produces a generic, unchallenged BRD. PRISM produces a *contested* one — where a regulator, a competitor, and a first-principles builder have all stress-tested your idea before you see a word.

---

## 2. Problem Statement

**The hackathon brief:** Build a scalable, multi-modal AI system using Google Gemini AI and integrated Google Cloud tools that can process real-time, fragmented data (text, images, and documents) and deliver accurate, context-aware, and explainable decisions in complex and dynamic environments.

**The real problem we're solving:** Early-stage founders and product teams waste weeks writing BRDs manually — interviewing stakeholders, documenting requirements, formatting documents. Existing AI tools generate one-shot, unchallenged, context-free documents. The output is generic because the process is shallow.

PRISM solves this by:
1. Accepting any form of input (text, voice, images, documents)
2. Grounding every decision in live real-world data (news, market, regulatory, cultural)
3. Running six expert perspectives simultaneously and letting them compete
4. Making the disagreement itself visible as risk signal
5. Explaining every requirement with a data citation and confidence score

---

## 3. Target Audience

**Primary:** Early-stage founders preparing for pre-seed or seed fundraising who need investor-grade BRDs but cannot afford a consultant.

**Secondary:** Product managers in mid-stage startups exploring new verticals who need rapid, structured requirements documentation.

**Tertiary:** Hackathon participants and student entrepreneurs in emerging markets (India, Southeast Asia) where regulatory complexity and local market data are hardest to surface.

---

## 4. Core Features — MVP (Demo Ready)

### 4.1 Conversational Intake
- Single chatbox: *"Tell me your idea — doesn't matter how messy."*
- Gemini Flash drives the conversation, asking only what's missing
- Dynamic follow-ups — no fixed form, no minimum word count
- Voice input via Web Speech API (Gemini Audio as fallback)
- File upload: images (Gemini Vision), PDFs (PyPDF2), Word docs (python-docx)
- Silent form-fill: as conversation progresses, structured fields extracted in background

**Intake extracts:**
- Business idea (core description)
- Target region (ISO 3166-1 alpha-2 — triggers context harvesting)
- Industry vertical
- Business stage (idea / prototype / mvp / growth)
- Budget range and constraints
- Success definition

### 4.2 Real-Time Context Harvesting
Fires in parallel the moment region is detected — while conversation continues.

| Source | Data | API |
|--------|------|-----|
| NewsAPI | Political climate, domain news, recent events | Free tier: 100 req/day |
| World Bank Open Data | GDP, ease of doing business, inflation, FDI | Unlimited (open) |
| Crunchbase Basic | Competitor funding, market activity | Free tier |
| Govt Open Data | Regional regulatory flags, industry-specific compliance | Open |
| Gemini Search Grounding | Cultural nuances, religious considerations, seasonal patterns | Free (within Gemini API) |

All 5 sources called via `asyncio.gather()`. A slow API never blocks the others.

### 4.3 Six-Agent Swarm
Six independent Gemini 1.5 Flash calls — same input, different system prompt injected.

| Agent | Persona | Mandate |
|-------|---------|---------|
| VC Investor | Silicon Valley seed-stage VC | Maximise fundability, TAM, moat |
| Lean Founder | Bootstrapped founder, $5K budget | Ship MVP in 4 weeks, cut everything else |
| Enterprise CTO | Risk-averse, Fortune 500 background | Scalability, compliance, security-first |
| UX Researcher | User-obsessed, ethnographic lens | User pain points, adoption barriers, accessibility |
| Regulator | Government policy expert | Legal compliance, regulatory landmines, ethical scrutiny |
| Adversarial Competitor | Well-funded rival trying to kill this idea | Identifies every weakness and gap |

All 6 run simultaneously. No coordination. No shared memory. Each produces a complete, independent BRD.

### 4.4 Weighted Evaluator
Single Gemini 1.5 Pro call. Scores all 6 BRDs across 5 weighted criteria.

| Criterion | Weight | Data Source |
|-----------|--------|-------------|
| Feasibility | 25% | World Bank data, stated constraints |
| Market Timing | 20% | NewsAPI, Crunchbase funding data |
| Regulatory Safety | 20% | Govt open data, regional compliance flags |
| User Adoption | 20% | Cultural context, UX research signals |
| Competitive Moat | 15% | Competitor analysis, market gap data |

Every score includes a one-line data citation. Not opinion — evidence.

### 4.5 Merge Engine
- Winning BRD (highest composite score) becomes the base
- Every other BRD scanned section by section
- Any section scoring higher than the winning BRD's equivalent → transplanted in
- Result: a BRD stronger than what any single agent could produce alone
- Every section carries a lineage tag: source agent + confidence score + data citation

### 4.6 Divergence Heatmap
- Calculates standard deviation of per-section scores across all 6 agents
- Normalised to 0–100 risk scale
- High divergence = high disagreement = high risk area of the business
- Visualised as animated bars per section
- Tooltip: "4 of 6 agents disagreed here — this section carries the highest risk"

### 4.7 Investor Readiness Score
- Single 0–100 score with weighted breakdown
- Gap flags: specific items pulling the score down with action items
- Colour coded: green >70, amber 50–70, red <50
- Animated count-up on reveal

### 4.8 Failure Mode Simulation
Agent 6 (Adversarial) output processed into top 3 failure modes:
- Title + probability percentage + description + pre-built mitigation
- Backed by real data from context harvester (e.g., "competitor raised $2M doing this exact thing")
- Lives in the BRD's Risk Register section

### 4.9 Assumption Flagging
Every hidden assumption in the final BRD surfaced:
- The assumption statement
- Confidence rating (high / medium / low)
- Evidence (or lack thereof) from context data
- Recommended action to validate

### 4.10 Stakeholder Export Views
Same BRD, three different PDFs generated from one Gemini call:
- **Investor View:** Lead with market, TAM, timing, moat. Soften technical complexity.
- **Technical View:** Lead with architecture, functional requirements, API dependencies.
- **Regulatory View:** Lead with legal framework, data handling, compliance, risk mitigation.

---

## 5. Roadmap Features (PPT / Future)

These are architected for but not built in the hackathon demo:

- **Pivot Suggester** — if score < 60, generates 3 concrete pivots with projected scores
- **Confidence Decay Monitor** — BRD freshness tracking; alerts when context has gone stale (new news, new competitor, regulatory change)
- **BRD Versioning** — user returns with same idea 3 months later; diff view shows what changed
- **Team Role Recommender** — recommends first hires and roles to skip based on what the BRD requires
- **Multi-Language Output** — BRD in local language auto-detected from target region
- **Voice BRD Walkthrough** — AI narrates the BRD section by section

---

## 6. API Contract Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/intake/session` | POST | Create new session |
| `/intake/session/{id}` | GET | Get session status |
| `/intake/chat` | POST | Submit a conversation turn |
| `/intake/upload` | POST | Upload image / PDF / doc |
| `/generate` | POST | Trigger BRD generation |
| `/generate/stream/{id}` | GET | SSE stream — live agent status |
| `/brd/{id}` | GET | Retrieve final merged BRD |
| `/brd/{id}/pdf` | GET | Download PDF (view param: investor / technical / regulatory) |

Full API contract with request/response schemas: see `SCHEMA.md`.

---

## 7. Success Metrics (Demo)

| Metric | Target |
|--------|--------|
| End-to-end BRD generation | < 50 seconds P95 |
| Context harvester (5 APIs) | < 8 seconds |
| Swarm (6 Flash calls) | < 20 seconds |
| Evaluator + Merge (2 Pro calls) | < 20 seconds |
| BRD quality vs. single-agent output | Demonstrably richer — show side by side |
| Concurrent demo sessions | 5 simultaneous |

---

## 8. Non-Functional Requirements

- **Cost:** 100% free tier. 20 Gemini API keys rotated. World Bank, Gemini Grounding, GCS, BigQuery all within free limits.
- **Availability:** Demo-grade — single region, no DR required.
- **Security:** No PII stored. Session-scoped access only. API keys never logged. File uploads validated by MIME type via magic bytes.
- **Accessibility:** WCAG 2.1 AA for all interactive elements. All agent states communicated via colour + text label (never colour alone).
- **Performance:** No layout shift after initial render. Skeleton states at fixed dimensions. Canvas animations use `devicePixelRatio` for HiDPI.
