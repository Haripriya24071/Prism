# Ritika — QA, Documentation and Demo

**Owns:** `backend/tests/`, `fixtures/`, `.env.example`, documentation review, PPT, demo script, demo video
**Does not touch:** application code. Report bugs to the owner with a reproduction.
**Governing docs:** [PRD.md](../../PRD.md) (success metrics), [RULES.md](../../RULES.md), [SCHEMA.md](../../SCHEMA.md)

QA starts in Phase 0, not at the end. Phases are gated by exit criteria, not dates.

---

## Phase 0 — Fixtures and Test Foundation (unblocks Swapnil)

| # | Deliverable | Notes |
|---|-------------|-------|
| 0.1 | `fixtures/`: realistic JSON for intake package, six agent outputs, score matrix, merged BRD with lineage, heatmap, investor readiness (one high score, one below 60), failed-agent case | must validate against SCHEMA.md. Swapnil needs these at the start of his Phase 1 |
| 0.2 | SSE fixture: the full event sequence from ARCHITECTURE.md as a replayable file | |
| 0.3 | pytest setup: `backend/tests/`, conftest, mypy config, how to run | |
| 0.4 | `.env.example` for backend and frontend covering every variable in CONTRIBUTING.md, with a one-line comment each | RULES.md: no undocumented vars |
| 0.5 | Review SCHEMA, ARCHITECTURE, PRD for contradictions and send them to the team | known open items: model names (Gemini 1.5 vs 3.5), `divergence_heatmap_data` missing from the ARCHITECTURE persistence diagram, Pivot Suggester listed as roadmap in PRD but in the data flow in ARCHITECTURE |

**Exit:** fixtures validate against Zahid's Pydantic models. Swapnil confirms he can render from them.

---

## Phase 1 — Tests Alongside Development

Write tests as each module lands. Mock all external HTTP and Gemini calls.

| # | Deliverable | File |
|---|-------------|------|
| 1.1 | Intake: extraction, region allowlist rejection, industry sanitising, upload MIME rejection by magic bytes | `test_intake.py` |
| 1.2 | Context: each client's success, timeout, malformed response. Harvester with one source failing | `test_context.py` |
| 1.3 | Storage: path derived only from session ID, lowercase, existence checks | `test_gcp.py` |
| 1.4 | Security: non-UUID session ID rejected on every route, no key in logs | `test_security.py` |

**Exit:** tests run green in under a minute with no network. Each test file stays under 400 lines (ARCH-007).

---

## Phase 2 — Core Pipeline Tests

| # | Deliverable | File |
|---|-------------|------|
| 2.1 | Swarm: all six fire, partial failure (4 of 6) continues, key rotation skips empty slots and retries on 429 | `test_swarm.py` |
| 2.2 | Evaluator: weights sum to 100%, uncited scores rejected | `test_evaluator.py` |
| 2.3 | Merger: highest base chosen, higher-scoring section transplanted, lineage present | `test_evaluator.py` or `test_merger.py` |
| 2.4 | Heatmap and investor score: fixed inputs with hand-computed expected values | `test_output.py` |
| 2.5 | SSE: events arrive in order and the stream closes | `test_sse.py` |

**Exit:** coverage includes the failure paths, not only the happy path. Hand-computed heatmap and score values match.

---

## Phase 3 — Integration and Frontend QA

| # | Deliverable | Notes |
|---|-------------|-------|
| 3.1 | End-to-end script: idea in, BRD out, against the real backend | records timings against PRD targets |
| 3.2 | Performance run: total under 50s, harvester under 8s, swarm under 20s, evaluator plus merge under 20s | report P95 over at least 10 runs |
| 3.3 | Five concurrent sessions | PRD success metric |
| 3.4 | Frontend checklist: keyboard-only pass, reduced motion, three breakpoints, voice in Chrome, upload rejection messages, failed-agent state | against RULES.md UI rules |
| 3.5 | Bug log with owner, reproduction steps, severity | one file in `docs/` |

**Exit:** a written report of timings and open bugs. No unowned bugs.

---

## Phase 4 — Presentation and Demo

| # | Deliverable | Notes |
|---|-------------|-------|
| 4.1 | PPT structure: problem, why one AI call fails, the swarm, grounded data, merge with lineage, heatmap, score, architecture, roadmap (confidence decay, versioning, multi-language, voice walkthrough) | roadmap items are labelled as not built |
| 4.2 | Side-by-side slide: single-agent BRD versus PRISM BRD on the same idea (PRD success metric) | generate this early from real output |
| 4.3 | Demo script: two ideas, one with a clear region, one messy and voice-driven. Timed, with exact words to say | |
| 4.4 | Fallback plan: a pre-recorded run and cached fixtures if the network or quota fails | agree the trigger for switching with the team |
| 4.5 | README review: setup steps actually work from a clean clone | do this on a machine that has never run the project |

**Exit:** script timed under the slot length. Fallback tested. README verified from a clean clone.

---

## Phase 5 — Rehearsal and Recording

- Full rehearsals with the whole team, minimum three, on the deployed environment
- Pre-warm NewsAPI cache and confirm key pool health before each rehearsal
- Record the demo video from a successful run
- Feature freeze check: nothing changes after the final rehearsal without a retest

**Exit:** three consecutive clean rehearsals. Video recorded. Slides final.

---

## Dependencies

| Need | From | By |
|------|------|----|
| Pydantic models to validate fixtures | Zahid | end of Phase 0 |
| Working modules to test | all | as they land |
| Deployed environment | Zahid | Phase 3 |

## Risks

- **Fixtures drift from the real output.** Regenerate them from a real run once Phase 3 lands.
- **Quota during rehearsal.** NewsAPI and Gemini Pro run out. Plan the rehearsal budget.
- **QA squeezed to the end.** The phase plan prevents this only if tests are written as modules land.
