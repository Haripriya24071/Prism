# Swapnil — Frontend + Persona Prompts

**Owns:** `frontend/`, `backend/agents/personas.py`, `backend/agents/prompts.py`, UI/UX loading animations.  
**Does not touch:** backend core or GCP integration files. Request changes from the owner (see [CONTRIBUTING.md](../../CONTRIBUTING.md)).  
**Governing docs:** [DESIGN.md](../../DESIGN.md), [RULES.md](../../RULES.md) (ARCH-005/006/011/012, UI-001 to UI-020), [SCHEMA.md](../../SCHEMA.md)

Phases are gated by exit criteria, not dates. Do not start a phase until the previous exit criteria are met.

---

## Current Status Overview
- **Phase 0 (Foundation & Contracts):** ✅ 100% Complete. React 18, Vite, design tokens, Tailwind config, routing skeleton operational.
- **Phase 1 (UI Components):** ✅ 100% Complete. `ChatBox`, `AgentGrid`, `AgentCard`, `ScoreCard`, `ScoreRing`, `DivergenceHeatmap`, `BRDViewer` built.
- **Phase 2 (Motion & Interactive States):** 🟡 90% Complete. Framer Motion transitions implemented. Handshake portal loading animation on deck.
- **Phase 3 (Live Backend Integration):** 🟡 85% Complete. SSE streaming hooked via `useSSE.js`, API service hooked via `api.js`. Live local test verified.
- **Phase 4 (Persona Prompts):** ✅ 100% Complete. `prompts.py` updated and calibrated to produce structured 6-section JSON with citation tags.

---

## Phase 0 — Foundation and Contracts (Completed)

| # | Deliverable | Location | Status |
|---|-------------|----------|--------|
| 0.1 | Vite + React 18 scaffold, Tailwind 3, ESLint config, `.env.example` entry `VITE_API_BASE_URL` | `frontend/` | ✅ Done |
| 0.2 | Design tokens: every colour, font, size, spacing and radius from DESIGN.md as CSS custom properties | `src/index.css`, `tokens.css` | ✅ Done |
| 0.3 | Tailwind config mapped to tokens (no raw hex anywhere, UI-001) | `tailwind.config.js` | ✅ Done |
| 0.4 | Review Zahid's Pydantic models and SSE event shapes. Confirm they carry everything the UI needs | `models/` review | ✅ Done |
| 0.5 | Route skeleton: `IntakePage`, `GenerationPage`, `ResultsPage`, session state via React Context | `src/pages/`, `src/hooks/` | ✅ Done |

**Exit Criteria:** `npm run lint` and `npm run build` pass. Tokens render a test page. Contract review signed off.

---

## Phase 1 — UI Components Against Mocks (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 1.1 | `ChatBox`: textarea with `sr-only` label, send, attach, AI bubbles | Accessible intake with rich dark mode aesthetics | ✅ Done |
| 1.2 | `useSSE` hook, closes the `EventSource` on unmount | Reconnect backoff, event dispatching for swarm | ✅ Done |
| 1.3 | `AgentGrid` + `AgentCard`: CSS Grid, persona accents, status chips | Live visual indicators for each of the 6 agents | ✅ Done |
| 1.4 | Skeleton states at exact loaded dimensions | Zero layout shift during SSE hydration | ✅ Done |
| 1.5 | `ScoreCard` + `ScoreRing`: SVG ring, count-up, green/amber/red thresholds | Real-time animated investor score display | ✅ Done |
| 1.6 | `DivergenceHeatmap`: 5 rows, `data-risk` drives colour, tooltip text | Visual risk radar highlighting agent debate | ✅ Done |
| 1.7 | `BRDViewer`: accordion, source chip, confidence, lineage block | Deep inspection of synthesised requirements | ✅ Done |

**Exit Criteria:** All three pages render from fixtures end-to-end. Keyboard-only walkthrough works with visible focus. `aria-live="polite"` on updates.

---

## Phase 2 — Motion, Loading Screens & Animation Polish (Active)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 2.1 | Framer Motion page and agent-card variants from DESIGN.md | `transform` + `opacity` only (UI-014) | ✅ Done |
| 2.2 | GSAP heatmap `scaleX` stagger, score count-up | Cleanup on unmount, kill timelines | ✅ Done |
| 2.3 | **Handshake Portal Loading Animation (`src/components/ui/HandshakeLoader.jsx`)** | Stylized 2D portal handshake with floating financial/growth badges (`$`, `%`, heart, checkmark, chart) communicating founder-market fit | 🔄 In Progress |
| 2.4 | `prefers-reduced-motion` path for every animation | UI-013 compliance | ✅ Done |
| 2.5 | `useVoiceInput` (Web Speech API), `VoiceButton` with recording state | Feature-detected, active in Chrome | ✅ Done |

**Exit Criteria:** Handshake loader renders smoothly without frame drops. Reduced-motion check respected. No console warnings.

---

## Phase 3 — Real Backend Integration (Active)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 3.1 | Swap fixtures for live API: session, chat, upload, generate, SSE, BRD | Unified in `src/api.js` | ✅ Done |
| 3.2 | Error and failed-agent states: failed agent card, retry-able error modal | UI-007 | ✅ Done |
| 3.3 | Stakeholder view selector + PDF download button | Calls `GET /brd/{id}/pdf?view=` | 🟡 Hooked (Pending Haripriya PDF verify) |
| 3.4 | Pivot suggestions block in `ScoreCard` | Displayed when `pivot_triggered == true` (score < 60) | ✅ Done |
| 3.5 | CORS and env check against backend | Tested on `http://localhost:8000` | ✅ Done |

**Exit Criteria:** A full end-to-end run from idea submission to live swarm deliberation and scorecard works seamlessly.

---

## Phase 4 — Persona Prompts & Calibration (Completed)

| # | Deliverable | Notes | Status |
|---|-------------|-------|--------|
| 4.1 | `personas.py`: Six persona definitions and constraint axes per PRD 4.3 | VC, Lean Founder, CTO, UX Researcher, Regulator, Adversarial | ✅ Done |
| 4.2 | `prompts.py`: Six system prompts enforcing structured 6-section JSON with source citation tags `[SOURCE: ...]` | Calibrated for Gemini 2.0 Flash JSON output | ✅ Done |
| 4.3 | Live Prompt Execution: Run sample idea through 6-agent swarm | Tested with 12-key Gemini pool; 5/5 active agents produced complete BRDs | ✅ Done |
| 4.4 | Divergence spread check | Ensured distinct perspectives across feasibility, timing, and regulatory safety | ✅ Done |

**Exit Criteria:** High divergence spread across personas; valid JSON output parsed into `AgentOutput` models.

---

## Phase 5 — Demo Polish & Freeze (Final Milestone)

- Final responsive layout verification at 768px, 1024px, and 1440px breakpoints.
- Lighthouse accessibility pass (contrast tokens, focus rings).
- Strip debug `console.log` statements.
- Two clean rehearsal walkthroughs with Ritika using the demo script.

**Exit Criteria:** Clean build, zero visual glitches, timed demo under 3 minutes.
