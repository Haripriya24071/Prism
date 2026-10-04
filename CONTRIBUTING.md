# PRISM — Team Contribution & Development Guide

---

## 1. Team Ownership & Responsibilities

Each team member owns defined modules with clear boundaries. Cross-boundary modifications require coordination with the respective owner. Detailed phased roadmaps are located in `docs/roadmap/`:
- [SWAPNIL.md](docs/roadmap/SWAPNIL.md) — Frontend Architecture, UI Components, Animation, System Prompts.
- [ZAHID.md](docs/roadmap/ZAHID.md) — Backend Core, FastAPI App, Key Pool Orchestration, Evaluation Rubric.
- [HARIPRIYA.md](docs/roadmap/HARIPRIYA.md) — External Context Harvester APIs, BigQuery Tables, Cloud Storage, PDF Export.
- [RITIKA.md](docs/roadmap/RITIKA.md) — QA Test Suites, Pitch Deck (PPT), Demo Script, Video Fallback.

---

## 2. Local Development Environment

### 2.1 Backend Setup
1. Activate the Python virtual environment:
   ```bash
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
2. Configure `backend/.env`:
   ```env
   # Add your Google AI Studio Gemini API keys (up to 20 keys supported):
   GEMINI_API_KEY_1=your_gemini_key_here
   GEMINI_FLASH_MODEL=gemini-flash-latest
   GEMINI_PRO_MODEL=gemini-flash-latest

   # GCP Project Configuration:
   GCP_PROJECT_ID=prism-hackathon-510523
   GCS_BUCKET_NAME=prism-outputs
   BIGQUERY_DATASET=prism_data
   GOOGLE_APPLICATION_CREDENTIALS=./prism-hackathon-510523-489baa57ba00.json
   ```
3. Start the backend development server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *Interactive OpenAPI docs: `http://localhost:8000/docs`*

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
   .venv/bin/python -c "import backend.main; print('Import check passed!')"
   ```

2. **Verify Swarm & Key Pool Health:**
   ```bash
   .venv/bin/python -c "
   import backend.config as cfg
   print('Active keys:', len(cfg._KEYS))
   m = cfg.get_flash_model()
   res = m.generate_content('Verify PRISM')
   print('LLM Response:', res.text.strip())
   "
   ```

3. **Frontend Lint & Build:**
   ```bash
   cd frontend
   npm run build
   ```

---

## 4. Git Branching & Commit Discipline

- **Branch Naming:**
  - `feat/feature-name` (e.g. `feat/handshake-loader`)
  - `fix/bug-description` (e.g. `fix/swarm-timeout`)
  - `docs/doc-update`
- **Commit Messages:**
  - Use clear imperative verbs: `Add HandshakeLoader animation to generation screen`, `Fix BigQuery fire-and-forget logging`.
  - Never commit raw API keys, private keys, or credentials to Git. Ensure `.env` is ignored in `.gitignore`.
