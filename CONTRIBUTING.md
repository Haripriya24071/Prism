# PRISM — Team Contribution & Development Guide

---

## 1. Team Ownership & Responsibilities

Detailed phased roadmaps are located in `docs/roadmap/`:
- [SWAPNIL.md](docs/roadmap/SWAPNIL.md) — Frontend Architecture, UI Components, Animation, System Prompts.
- [ZAHID.md](docs/roadmap/ZAHID.md) — Backend Core, FastAPI App, Key Pool Orchestration, Evaluation Rubric.
- [HARIPRIYA.md](docs/roadmap/HARIPRIYA.md) — External Context Harvester APIs, BigQuery Tables, Cloud Storage, PDF Export.
- [RITIKA.md](docs/roadmap/RITIKA.md) — QA Test Suites, Pitch Deck (PPT), Demo Script, Video Fallback.

## Branch Strategy

All commits go directly to `main`. This is a hackathon — no feature branches, no PRs.

Before every push:
```bash
git pull --rebase origin main
```
Then push:
```bash
git push origin main
```
If a rebase conflict occurs, resolve it file by file. Never use `git push --force`.

## File Ownership

Each teammate owns specific files. Only edit files you own unless you have explicitly agreed a change with the owner in the team chat.

| Owner | Files / Folders |
|-------|----------------|
| Zahid (Backend Lead) | `backend/` — all Python files |
| Swapnil (Frontend Lead) | `frontend/` or `src/` — all UI files |
| Haripriya (GCP + Infra) | GCP project config, `backend/gcp/`, deployment scripts |
| Ritika (QA + Slides) | `tests/` additions, presentation deck, demo script |

If you need a change in someone else's files, message them first and let them make the commit.

---

## 2. Local Development Environment

### 2.1 Backend Onboarding (for teammates reading this for the first time)

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # fill in GCP_PROJECT_ID and credentials
uvicorn main:app --reload --port 8000
```

Check it works:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok","version":"0.1.0"}
```

Run tests:
```bash
python -m pytest tests/ -v
# Expected: 129 passed
```

### 2.2 Frontend Setup
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Frontend interface: `http://localhost:5173`*

---

## 3. Code Standards & Pre-Commit Verification

Before submitting changes or committing code, run these verification steps:

1. **Verify No Circular Imports:**
   ```bash
   python -c "import main; print('Import check passed!')"
   ```

2. **Frontend Lint & Build:**
   ```bash
   cd frontend
   npm run build
   ```

---

## Commit Discipline

- One logical change per commit. Never stage unrelated files together.
- Format: `type(scope): description`
  - `feat(backend): add ...`
  - `fix(backend): correct ...`
  - `docs: update ...`
  - `test(backend): add ...`
  - `refactor(backend): ...`
- Before committing Python files: `python -c "import <module>"` must exit 0.
- Never commit `.env`, `venv/`, `__pycache__/`, or `*.pyc`.
- Run `mypy backend/ --ignore-missing-imports --python-version 3.11` before pushing — must be clean.

---

## Demo Day Checklist (run the night before)

```bash
# 1. Pull latest
git pull --rebase origin main

# 2. Confirm tests pass
cd backend
python -m pytest tests/ -v

# 3. Pre-warm NewsAPI cache
python demo_runner.py --prewarm

# 4. Dry-run all three scenarios (requires real GCP credentials)
python demo_runner.py IndiaFintechSMB
python demo_runner.py SingaporeEdTechB2B
python demo_runner.py USHealthTechConsumer

# 5. Start the server
uvicorn main:app --port 8000

# 6. Confirm health endpoint
curl http://localhost:8000/health
```

---

## What Each Backend Module Does (quick reference)

| Module | Purpose |
|--------|---------|
| `main.py` | FastAPI app — 8 endpoints, Vertex AI lifespan init |
| `pipeline.py` | Full BRD pipeline — 14 steps, SSE progress events |
| `config.py` | All env vars, Vertex AI ADC init, model helpers |
| `session_store.py` | In-memory session CRUD with UUID4 IDs and TTL |
| `sse_manager.py` | Per-session asyncio queues for live SSE streaming |
| `intake/` | Conversation, vision, document, field extraction |
| `context/` | 5 parallel data sources + harvester orchestrator |
| `agents/` | 6 persona definitions, prompt builder, swarm |
| `evaluation/` | Rubric, Gemini Pro scorer, BRD merge engine |
| `output/` | Heatmap, investor score, assumptions, PDF export |
| `gcp/` | GCS read/write, BigQuery logging, local dev fallback |
| `demo_config.py` | 3 demo scenarios with talking points |
| `demo_runner.py` | End-to-end dry-run CLI |
