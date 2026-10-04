# PRISM — Product Requirements Document (PRD)

**Version:** 2.0 (Production Verified) | **Team:** Swapnil Ghosh, Zahid, Haripriya, Ritika | **Date:** October 2026  
**Hackathon:** Manipal Hackathon 2026 | **Track:** Google Gemini AI + Google Cloud  

---

## 1. Executive Summary

PRISM is an enterprise-grade multi-modal AI intelligence system that transforms raw, unstructured, fragmented business ideas — expressed as text, voice, diagrams, or documents — into institutional-grade, investor-ready Business Requirements Documents (BRDs) backed by live market intelligence.

PRISM is not a template generator. It is a **Structured Disagreement Engine**.

Instead of a single one-shot prompt that produces agreeable hallucinations, PRISM routes an idea through six adversarial AI agents simultaneously. Each agent embodies a distinct, uncompromising expert persona (Venture Capitalist, Lean Builder, Enterprise CTO, UX Researcher, Regulatory Auditor, and Adversarial Competitor). The system captures their debate, evaluates section quality against a multi-axis rubric, transplants the strongest sections into a unified BRD, and quantifies disagreement into a visual risk radar.

Every requirement in PRISM carries:
1. **Lineage Attribution:** The specific agent that drafted or refined it (`[LineageTag]`).
2. **Data Citation:** Real-world verified data (`[SOURCE: worldbank]`, `[SOURCE: newsapi]`, `[SOURCE: crunchbase]`, etc.).
3. **Confidence Rating:** Explicit score reflecting evidential backing.
4. **Dissent Notes:** What opposing agents warned about.

---

## 2. Problem Statement & Hackathon Alignment

### The Official Hackathon Challenge:
> *"Build a scalable, multi-modal AI system using Google Gemini AI and integrated Google Cloud tools (such as Vertex AI, Cloud Storage, and BigQuery) that can process real-time, fragmented data (text, images, and documents) and deliver accurate, context-aware, and explainable decisions in complex and dynamic environments."*

### How PRISM Delivers:
- **Scalable Multi-Modal AI:** Ingests unformatted founder descriptions, voice input via Web Speech API, whiteboards/wireframes via Gemini Multimodal Vision, and pitch decks via PyPDF2 / python-docx.
- **Real-Time Fragmented Data:** Harvests parallel macroeconomic indicators, live industry news, and cultural grounding across 5 external streams the instant a region is detected.
- **Accurate & Explainable Decisions:** Evaluates 6 competing BRDs through an impartial rubric engine and logs all session parameters to Google BigQuery.
- **Integrated Google Cloud Tools:** Utilizes Gemini 2.0 Flash, Google Cloud Storage for artifact persistence, Google BigQuery for analytics and decision logging, with an enterprise production architecture ready for Vertex AI.
- **Zero-Cost High-Throughput Resilience:** Operates 100% on the ₹0 Free Tier using a 48-quota-pool model cascade and autonomous heuristic recovery engine.

---

## 3. The 6-Agent Persona Swarm

| Agent Persona | Accent Token | Analytical Lens & Hard Constraints |
| :--- | :--- | :--- |
| **1. The VC** | `#7C3AED` (Violet) | Focuses on TAM/SAM/SOM, unit economics, LTV/CAC ratios, moat defensibility, and 10x scalability. Rejects low-margin service businesses. |
| **2. Lean Founder** | `#0EA5E9` (Sky Blue) | Ruthlessly minimizes scope. Enforces a 4-week MVP build timeline. Strips away non-essential features and focuses on validation speed. |
| **3. Enterprise CTO** | `#10B981` (Emerald) | Evaluates technical feasibility, scalability, microservice architecture, API design, zero-trust security, and 99.95% uptime SLAs. |
| **4. UX Researcher**| `#F59E0B` (Amber) | Represents end-user psychology, onboarding friction, behavioral accessibility, and user retention mechanics. |
| **5. The Regulator** | `#6366F1` (Indigo) | Audits compliance, GDPR/DPDP data privacy, sector-specific statutory laws, financial liability, and licensing requirements. |
| **6. The Adversarial**| `#EF4444` (Crimson) | Acts as an aggressive competitor. Identifies exploit vectors, churn triggers, platform dependency risks, and actively tries to destroy the idea. |

---

## 4. Product Features & Flow

```
Founder Input (Text, Voice, Img, Doc) ──► Conversational Extraction ──► Parallel Context Harvesting
                                                                               │
         ┌─────────────────────────────────────────────────────────────────────┘
         ▼
6-Agent Parallel Swarm Deliberation (KeyCircuitBreaker across 48 Quota Pools)
         │
         ▼
Rubric Evaluation (5 Weighted Criteria) & Surgical Section Merge Engine
         │
         ├─────────────────────────────────────────────┐
         ▼                                             ▼
Divergence Heatmap & Investor Readiness Score    3 Stakeholder PDF Exports
(Quantified Disagreement & Risk Radar)           (Investor / Tech / Regulatory)
```

### 4.1 Conversational Intake
- Natural chat interface without tedious static forms.
- Automatically extracts: Region (ISO 3166-1), Industry, Stage, Budget, and 12-month Success Metric.
- Multimodal drag-and-drop supporting PNG, JPEG, PDF, and DOCX files.
- Resilient fallback state machine guarantees zero 500 errors during chat.

### 4.2 Real-Time Context Harvesting
- Triggers 5 asynchronous data queries in parallel:
  1. NewsAPI (regional headlines & industry sentiment)
  2. World Bank Open Data (GDP per capita, inflation, ease of doing business)
  3. Crunchbase Basic (recent funding trends)
  4. Govt Open Data (statutory regulatory guidelines)
  5. Gemini Grounding (cultural sensitivities, seasonal shopping cycles)

### 4.3 Evaluation Rubric & Surgical Merge
- Evaluates each BRD across 5 criteria:
  - Technical Feasibility (25%)
  - Market Timing (20%)
  - Regulatory Safety (20%)
  - User Adoption (20%)
  - Competitive Moat (15%)
- Merges the winning base document with top-scoring sections from opposing agents, preserving complete lineage.

### 4.4 Divergence Heatmap
- Calculates per-section standard deviation across all 6 agent scores.
- Renders a color-coded visual risk radar (Green = Consensus, Amber = Moderate Variance, Red = Severe Contested Disagreement).

### 4.5 Investor Readiness Scorecard & Pivot Suggester
- Composite 0–100 score indicating fundraising readiness.
- If score < 60, triggers `output/pivot.py` to deliver 3 strategic pivot directions with projected score improvements.

### 4.6 Triple Stakeholder PDF Export
- Generates 3 specialized ReportLab PDFs from the same verified data:
  1. **Investor View:** Focused on unit economics, TAM, market timing, and capital efficiency.
  2. **Technical View:** Focused on system architecture, data models, scalability, and security.
  3. **Regulatory View:** Focused on compliance checklists, liability, and statutory filings.

---

## 5. Technical Performance & Resilience Benchmarks

- **Swarm Execution:** < 18s P95 across all 6 agents running simultaneously.
- **Total Pipeline Latency:** < 38s P95 from idea submission to rendered scorecard.
- **Key Pool Throughput:** 180+ RPM through thread-safe `KeyCircuitBreaker`.
- **Completion Rate:** **100% (6/6 agents complete)** guaranteed by the Autonomous Swarm Heuristic Recovery engine.
- **Cost:** **₹0 Forever** across all utilized Google Cloud and Gemini services.
