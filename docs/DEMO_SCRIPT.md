# PRISM — 3-Minute Live Hackathon Demo Playbook & Script

> **Lead Presenter:** Ritika / Swapnil  
> **Total Time Limit:** Exactly 3 Minutes (180 Seconds) + 2 Minutes Judge Q&A  
> **Target Audience:** Manipal Hackathon 2026 Evaluation Panel & Google Cloud Judges

---

## ⏱️ Exact 3-Minute Chronological Run-of-Show

```text
┌─────────────────┬─────────────────┬───────────────────────────┬─────────────────┐
│ 0:00 – 0:35     │ 0:35 – 1:15     │ 1:15 – 2:30               │ 2:30 – 3:00     │
│ The Crisis      │ Swarm & GCP     │ Live System Demonstration │ Judge Q&A       │
│ (Slides 1–2)    │ (Slides 3–4)    │ (Pitch Launchpad & Swarm) │ & Defense       │
└─────────────────┴─────────────────┴───────────────────────────┴─────────────────┘
```

---

## Act 1: The Crisis of "Agreeable AI" (0:00 – 0:35 • 35s)
*Visual: Slide 1 & Slide 2 from [pitch_deck.html](pitch_deck.html)*

### Speaker Delivery:
> "Good afternoon judges. We’ve all seen founders pitch brilliant-sounding startup ideas that collapse within 6 months. Why? Because when they used AI to write their PRD, the AI acted like a sycophantic yes-man.
> 
> If you give ChatGPT a flawed consumer lending or crypto idea, it writes a glowing 20-page document praising it. It never warns you about central bank interest rate shocks, GDPR liabilities, or Microsoft Copilot commoditization.
> 
> Single-prompt AI is an echo chamber.
> **We built PRISM: an autonomous swarm that replaces agreeable hallucinations with rigorous adversarial disagreement.**"

---

## Act 2: The Structured Disagreement Engine & GCP (0:35 – 1:15 • 40s)
*Visual: Slides 3 & 4 from [pitch_deck.html](pitch_deck.html)*

### Speaker Delivery:
> "PRISM doesn’t just query one LLM. We orchestrate **6 specialized, adversarial expert personas** running in parallel on Google Cloud:
> - **The VC** who demands 10x margins and network moats.
> - **The Lean Founder** who cuts scope down to a 4-week validation loop.
> - **The Enterprise CTO** who enforces zero-trust architecture and 99.95% SLAs.
> - **The UX Researcher** fighting onboarding friction.
> - **The Regulator** auditing statutory compliance.
> - And **The Adversary** actively hunting platform dependency risks.
> 
> Behind them sits our **Real-World Context Harvester**, pulling live NewsAPI headlines, World Bank economic data, Wikipedia geopolitical risk, and Forex rates.
> 
> Everything runs on **Vertex AI & Gemini 2.0 Flash**, persisting audit trails to **Google BigQuery** and validated blobs to **Cloud Storage**, with our **Autonomous Swarm Heuristic Recovery engine** guaranteeing 100% completion with zero crashes."

---

## Act 3: Live System Demonstration (1:15 – 2:30 • 75s)
*Visual: Live Browser Window at `http://localhost:5173/#pitch`*

### Action 1 (1:15 – 1:30 • 15s): Conversational Zero-Friction Intake & Voice AI
1. Switch tab to `http://localhost:5173/#pitch`.
2. Click the **Voice Mic Button** or click the quick starter card **"FinTech Compliance"** or type:
   > *"Autonomous AI code review and automated security auditing for enterprise GitHub pull requests in the US."*
3. **Point to the Live Swarm Calibration Matrix ribbon at the top:**
   > *"Notice how the founder never fills a clunky form. As we speak or type, PRISM's behind-the-scenes extractor identifies the Core Concept, sets Target Market to US, Sector to DevSecOps, and illuminates the calibration matrix in real time."*

### Action 2 (1:30 – 1:55 • 25s): The Swarm in Motion (HandshakeLoader & Real-Time SSE)
1. Click **`⚡ Run 6-Agent Swarm →`**.
2. **Explain the HandshakeLoader screen:**
   > *"The moment we trigger the swarm, our real-world harvesters pull live US macroeconomic and tech sector signals. 
   > Watch the 6 agent cards: each persona evaluates the thesis simultaneously through their own analytical lens. The CTO is auditing AST secret redaction; the Adversary is analyzing prompt injection attack vectors."*
3. Show the live deliberation thought bubbles updating via Server-Sent Events (SSE).

### Action 3 (1:55 – 2:30 • 35s): Results, Divergence Heatmap & Strategic Pivots
1. When the results screen appears, highlight the 3 core innovations:
   - **1. The Investor Readiness Score (e.g. 84/100, High Confidence):**
     > *"Here is our mathematical composite score across 5 objective rubric criteria: Technical Feasibility, Market Timing, Regulatory Safety, User Adoption, and Competitive Moat."*
   - **2. The Divergence Risk Heatmap:**
     > *"Look at this heatmap. Where you see high divergence (in red), that’s not an error—that’s a critical boardroom debate. The Regulator and Adversary flagged severe IP leakage risks that ChatGPT would have completely missed."*
   - **3. Section Lineage & 1-Click PDF Export:**
     > *"Every section in the master BRD has a `[LineageTag]` and citation proof. And with one click, we export customized executive PDFs for Investors, CTOs, or Compliance Officers."*

---

## 🎯 Fallback Demo Scenario: High-Risk Consumer FinTech (Pivot Suggester)
*Use this scenario if judges ask: "What happens if an idea is terrible?"*

- **The Pitch:** *"Peer-to-peer consumer payday lending on social media in Southeast Asia."*
- **What Happens:**
  1. The Regulator immediately flags severe statutory micro-lending licensing violations.
  2. The Adversary flags 75% fraud default rates and bot loan syndicates.
  3. The Investor Readiness Score drops to **42/100 (Pivot Advised)**.
  4. The **Strategic Pivot Suggester** activates, offering 3 validated alternative models:
     - *Pivot A: B2B Embedded Payroll Advance for Verified Employers.*
     - *Pivot B: Alternative Credit Underwriting API for Licensed Regional Banks.*
     - *Pivot C: Cross-Border Remittance Escrow via Open Banking.*

---

## 🛡️ Judge Q&A & Architecture Defense Cheat Sheet (2:30 – 3:00 • 30s)

### Q1: "How do you prevent the 6 agents from agreeing with each other?"
> **Answer:** "Every persona has a mutually exclusive analytical mandate and opposing loss functions encoded into their system prompts. For instance, the VC is forbidden from caring about 4-week scope; the Lean Founder is penalized if engineering runway exceeds 30 days; the Adversary is rewarded exclusively for finding lethal exploit vectors. Furthermore, our 5-axis rubric evaluator is completely decoupled from the agents that generated the draft."

### Q2: "What happens if Gemini rate limits (HTTP 429) during the live swarm?"
> **Answer:** "Swapnil engineered the `KeyCircuitBreaker` with 48 independent quota pools across 4 model tiers, plus per-thread client isolation. If an API key or upstream endpoint ever encounters a cooldown, our Autonomous Swarm Heuristic Recovery engine instantly synthesizes domain-grounded drafts. We guarantee a 100% completion rate across all 6 agents with zero pipeline crashes."

### Q3: "How does this utilize Google Cloud Platform?"
> **Answer:** "PRISM leverages GCP end-to-end:
> 1. **Vertex AI / Gemini 2.0 Flash:** High-throughput streaming inference.
> 2. **Google BigQuery:** Tamper-proof audit trails for compliance (`brd_runs`).
> 3. **Google Cloud Storage:** SHA-256 validated blob persistence with signed URLs.
> 4. **Cloud Run:** Auto-scaling serverless microservices."
