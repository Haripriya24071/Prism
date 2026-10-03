# Swapnil — Frontend + Persona Prompts

**Owns:** `frontend/`, `backend/agents/personas.py`, `backend/agents/prompts.py`
**Does not touch:** any other backend file. Request changes from the owner (see [CONTRIBUTING.md](../../CONTRIBUTING.md)).
**Governing docs:** [DESIGN.md](../../DESIGN.md), [RULES.md](../../RULES.md) (ARCH-005/006/011/012, UI-001 to UI-019), [SCHEMA.md](../../SCHEMA.md)

Phases are gated by exit criteria, not dates. Do not start a phase until the previous exit criteria are met.

---

## Phase 0 — Foundation and Contracts

| # | Deliverable | Location |
|---|-------------|----------|
| 0.1 | Vite + React 18 scaffold, Tailwind 3, ESLint config, `.env.example` entry `VITE_API_BASE_URL` | `frontend/` |
| 0.2 | Design tokens: every colour, font, size, spacing and radius from DESIGN.md as CSS custom properties | `src/styles/tokens.css` |
| 0.3 | Tailwind config mapped to tokens (no raw hex anywhere, UI-001) | `tailwind.config.js` |
| 0.4 | Review Zahid's Pydantic models and SSE event shapes. Confirm they carry everything the UI needs (lineage, dissent, assumptions, failure modes, heatmap, score, pivots) | review only |
| 0.5 | Route skeleton: `IntakePage`, `GenerationPage`, `ResultsPage`, session state via React Context | `src/pages/`, `src/hooks/useSession.js` |

**Exit:** `npm run lint` and `npm run build` pass. Tokens render a test page. Contract review signed off in writing by Zahid.

---

## Phase 1 — UI Against Mocks

Build every screen against Ritika's fixtures. No backend needed.

| # | Deliverable | Notes |
|---|-------------|-------|
| 1.1 | `ChatBox`: textarea with `sr-only` label, send, attach, AI bubbles | UI-008 |
| 1.2 | `useSSE` hook, closes the `EventSource` on unmount | ARCH-012. Test with a mock event emitter |
| 1.3 | `AgentGrid` + `AgentCard`: CSS Grid 3/2/1 columns, `data-agent` accent, status chip with colour **and** text | UI-007, UI-012, UI-019 |
| 1.4 | Skeleton states at exact loaded dimensions | UI-010 |
| 1.5 | `ScoreCard` + `ScoreRing`: SVG ring, count-up, green >70 / amber 50–70 / red <50 | threshold tokens, not inline colour |
| 1.6 | `DivergenceHeatmap`: 5 rows, `data-risk` drives colour, tooltip text | UI-018 |
| 1.7 | `BRDViewer`: accordion, source chip, confidence, lineage block, `AssumptionFlag`, dissent expander | no barrel files (ARCH-006) |

**Exit:** all three pages render from fixtures end to end. Keyboard-only walkthrough works with visible focus (UI-004). `aria-live="polite"` on status, heatmap and BRD updates (UI-009).

---

## Phase 2 — Motion and Voice

| # | Deliverable | Notes |
|---|-------------|-------|
| 2.1 | Framer Motion page and agent-card variants from DESIGN.md | `transform` + `opacity` only (UI-014) |
| 2.2 | GSAP heatmap `scaleX` stagger, score count-up | cleanup on unmount, kill timelines |
| 2.3 | `prefers-reduced-motion` path for every animation | UI-013 |
| 2.4 | `useVoiceInput` (Web Speech API), `VoiceButton` with recording state | feature-detect, hide button where unsupported |
| 2.5 | Voice fallback decision: if the Gemini Audio fallback is built, agree the upload endpoint with Zahid. If not, document it as unsupported on Firefox | decide here, not in Phase 4 |
| 2.6 | Optional: particle canvas background | `requestAnimationFrame` only, `pointer-events: none`, DPR sizing (ARCH-011, UI-015, UI-016). Cut first if slow |

**Exit:** animations pass the reduced-motion check. Voice works in Chrome. No console errors.

---

## Phase 3 — Real Backend Integration

| # | Deliverable | Notes |
|---|-------------|-------|
| 3.1 | Swap fixtures for the live API: session, chat, upload, generate, SSE, BRD | single `api` module, named exports |
| 3.2 | Error and failed-agent states: failed agent card, retry-able generation error, upload validation messages | UI-007 |
| 3.3 | Stakeholder view selector + PDF download | needs Haripriya's `/brd/{id}/pdf?view=` |
| 3.4 | Pivot suggestions block in `ScoreCard`, shown only if `pivot_triggered` | stretch dependency, hide cleanly if absent |
| 3.5 | CORS and env check against the deployed Railway URL | with Zahid |

**Exit:** a full run, idea to downloaded PDF, works against the real backend on local and on Vercel + Railway.

---

## Phase 4 — Persona Prompts (starts in Phase 1, runs in parallel)

You own the quality of the six agents. Zahid wires them in.

| # | Deliverable | Notes |
|---|-------------|-------|
| 4.1 | `personas.py`: six persona definitions and constraint axes per PRD 4.3 | data only, no logic, no I/O |
| 4.2 | `prompts.py`: six system prompts that force the agent to output the BRD JSON shape in SCHEMA.md (5 sections, assumptions, citations) | prompts must reference supplied context data by name so citations are real |
| 4.3 | Prompt test set: three sample ideas run through each persona, outputs compared | hand to Ritika for fixture capture |
| 4.4 | Divergence check: personas must produce meaningfully different scores. If agents converge, rewrite constraints, don't tweak wording | the heatmap depends on this |

**Exit:** on the three sample ideas, per-section score spread is visible and each output validates against the Pydantic `AgentOutput` model.

---

## Phase 5 — Polish and Demo Freeze

- Responsive check at 768 and 1024 breakpoints only (UI-011)
- Lighthouse accessibility pass. Fix contrast issues using verified token pairs only
- Remove all `console.log` (RULES.md General)
- Feature freeze agreed with team. After freeze: bug fixes only

**Exit:** `npm run lint` and `npm run build` clean. Demo path rehearsed twice with Ritika with no visual glitches.

---

## Dependencies

| Need | From | By |
|------|------|----|
| Pydantic models + SSE event spec | Zahid | end of Phase 0 |
| Mock fixtures (intake, agent outputs, score matrix, merged BRD, heatmap, score) | Ritika | start of Phase 1 |
| `/brd/{id}/pdf` | Haripriya | Phase 3 |
| Swarm wiring of personas/prompts | Zahid | Phase 4 |

## Risks

- **Animation scope creep.** Heatmap and score ring come first. Particles and per-card canvas are optional.
- **Web Speech API support.** Chrome and Edge only. The demo must run in Chrome.
