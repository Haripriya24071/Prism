# PRISM: Session Log (Integrations / Storage / Output role)

Covers everything from the moment `Prism-main.zip` was uploaded, through the step-by-step build in Antigravity, up to the GCP setup discussion.

**Repo:** `github.com/Haripriya24071/Prism` | **Working branch:** `hp/backend` | **Team:** Hari Priya (you), Zahid, Ritika, Swapnil

---

## 1. You asked: read the zip entirely and tell me my role

I read all 13 files in the repo (README, PRD, RULES, CONTRIBUTING, TECHSTACK, ARCHITECTURE, SCHEMA, DESIGN and the four roadmap files).

### Your role: Integrations, Storage and Output

Your plan is in `docs/roadmap/HARIPRIYA.md`.

**You own**
- `backend/context/`: five harvester clients (NewsAPI, World Bank, Crunchbase, government open data, Gemini Search Grounding) and `harvester.py`
- `backend/gcp/`: `storage.py` (Cloud Storage) and `bigquery.py`
- `backend/output/`: `assumptions.py`, `failure_sim.py`, `stakeholder.py`, `pdf_export.py`

**You don't touch:** `models/`, `main.py` (Zahid), `frontend/` (Swapnil). Ask the owner for changes there.

### Your phases (gated by exit criteria, not dates)

| Phase | What you do | Exit criteria |
|---|---|---|
| 0. Setup | Test all keys, confirm Crunchbase access, review Zahid's models, create bucket, dataset and four BigQuery tables | Every key works from a scratch script, models signed off, bucket and tables exist |
| 1. Harvester clients | One async client per source, typed result, never raises on bad response, input sanitising | Each client has a mocked test and a live call; a timeout returns an empty result |
| 2. Harvester + storage | `storage.py`, parallel blob reads, `harvester.py` with `asyncio.gather`, BigQuery logging | Context package in under 8s even with one source failing; rows appear in BigQuery |
| 3. Output layer | Assumption flagging, failure-mode simulation, three stakeholder views, three ReportLab PDFs | Three PDFs in under 3s with lineage and citations visible |
| 4. Resilience | Disable each source in turn, check keys never appear in logs, 5 concurrent sessions, free-tier quota | Five concurrent sessions complete without errors |
| 5. Freeze | Pre-warm cache for demo ideas, verify bucket permissions, bug fixes only | n/a |

### Things to watch
- `gcp/storage.py` is on the critical path: Zahid's swarm can't save outputs without it.
- Crunchbase's free API may not be usable; decide in Phase 0 and use a labelled static fallback if not.
- NewsAPI allows 100 requests a day; the cache has to work.
- Government data has no uniform source; scope to India plus one fallback region.

---

## 2. You asked: problems, and what's connected to Zahid and others (no branches, direct to main)

### Problems in the plan

**Affecting your work**
1. The Gemini wrapper has no agreed location. `context/` and `output/` can't import `agents/` (rule ARCH-001), so the wrapper has to live somewhere lower.
2. Your Gemini calls (grounding, assumptions, failure sim, stakeholder views) weren't counted in the latency budget or the Pro rate limit. Use Flash for the three post-merge calls.
3. "Three PDFs under 3s" ignores the stakeholder Gemini call; treat 3s as render time only.
4. Nobody clearly owned BigQuery writes for three of the four tables. You provide one `log_*` function per table and Zahid calls them.
5. Crunchbase's free tier may give no usable API.
6. NewsAPI's 100/day limit will run out during rehearsals; cache by region + industry and pre-warm.
7. PDF names conflicted between docs; go with SCHEMA (`output_investor/technical/regulatory.pdf`).

**Project-wide**
8. Model names were probably outdated (Gemini 1.5 in several places).
9. Rotating 20 API keys likely breaks Google's terms and looks bad on a slide.
10. Vertex AI was only named, not used, but the problem statement asks for it.
11. The PRD and ARCHITECTURE disagree on whether the Pivot Suggester is built or roadmap.

### What's connected to others

**You need from others**

| From | What | Why it blocks you |
|---|---|---|
| Zahid | Pydantic models (`ContextPackage`, `NewsItem`, `MarketData`, etc.) | Every client returns these types |
| Zahid | `config.py` entries (bucket, dataset, tables, timeouts, keys) | ARCH-009 forbids hardcoded names and you can't edit `config.py` |
| Zahid | `errors.py` and the Gemini wrapper | Typed failures and the grounding call |
| Zahid | The `/brd/{id}/pdf` route, the harvester call after region detection, the `context_ready` SSE event | He wires your code in |
| Ritika | Fixtures, tests, `.env.example` entries | Tell her each new env var |

**Others need from you**

| To | What | When |
|---|---|---|
| Zahid | `gcp/storage.py` (write, confirm, exists-check, lowercase paths) | Start of his Phase 2 (critical path) |
| Zahid | `context/harvester.py` returning a `ContextPackage` plus which sources succeeded | End of Phase 2 |
| Zahid | BigQuery `log_*` functions, fire-and-forget | Phase 2 |
| Swapnil | The shape of `ContextPackage` (field names are a contract for his prompts) | Early |
| Swapnil | PDF download and the three view names | Phase 3 |
| Ritika | Sample real outputs to refresh fixtures | After Phase 3 |

### Working directly on main (the rules we discussed)
- `git pull --rebase origin main` before every push, push small and often
- Edit only your own files; ask the owner for anything else
- Push stubs with signatures early so others can import them
- Run `python -c "import main"` and `mypy` before pushing
- Never commit `.env`, GCP credentials or API keys
- Agree contracts (models, signatures, SSE events) in writing before coding

(You later moved to your own branch `hp/backend`, which makes most of this safer.)

---

## 3. You asked: draft messages for the group and for Zahid

### Group message (issues found)

```
Hey team, I went through all the PRISM docs and roadmaps. Before we start pushing to main, here are the issues I found that we should settle first:

1. Gemini model names: docs say Gemini 1.5 in most places and 3.5 in TECHSTACK. 1.5 may be retired. @Zahid please check what actually resolves on our keys in Phase 0.

2. 20-key rotation: spreading calls across 20 keys to dodge rate limits likely breaks Google's terms, and it will look bad if a judge reads the slide. 6 Flash + 2 Pro per run fits normal limits anyway. Suggest we drop it from the PPT and docs.

3. Vertex AI is only named, not used. The problem statement explicitly asks for it. If we call Gemini through Vertex, that fixes this and the key issue too.

4. Extra Gemini calls aren't counted: assumptions, failure sim and stakeholder views add 3 calls after merge. They aren't in the 50s budget or the 2 RPM Pro limit. Proposal: use Flash for all three.

5. PDF names conflict: TECHSTACK/ARCHITECTURE say output.pdf, SCHEMA says output_investor/technical/regulatory.pdf. Let's go with SCHEMA.

6. Pivot Suggester: PRD calls it roadmap, ARCHITECTURE has it in the data flow. Is it built or only on the slide? @Ritika this changes what the PPT claims.

7. Crunchbase free tier may not give a usable API. I'll confirm in Phase 0. If not, we use a labelled static fallback and say so in the demo.

8. NewsAPI is 100 requests/day and rehearsals will burn it. I'll cache by region + industry and pre-warm for the demo ideas. Please don't run big test loops against the live key.

Since we all push straight to main:
- git pull --rebase origin main before every push
- only edit files you own; ask the owner for changes elsewhere
- push stubs with signatures early so others can import them
- run python -c "import main" and mypy before pushing
- never commit .env or any keys

Let's agree the contracts (models, function signatures, SSE events) in this chat before anyone writes code. Thoughts?
```

### Message to Zahid (contracts needed)

```
Hey Zahid, I'm starting Phase 0 on the integrations side. A few things I need from you before I write real code, since you own models, config and main.py:

1. Gemini wrapper location: my grounding client (context/) and my output modules (assumptions, failure_sim, stakeholder) all call Gemini. ARCH-001 stops context/ and output/ importing agents/. Where will your wrapper live so I can import it? Suggestion: a small shared module under gcp/ or its own file lower in the dependency chain. Can you share the function signature (async, takes prompt + model name, returns parsed JSON)?

2. Models: please publish ContextPackage, NewsItem, MarketData and the assumption / failure-mode shapes early, even before the app runs. I'll review against what each API really returns and sign off. One question: should competitors from Crunchbase be a separate list of typed objects, like in SCHEMA?

3. config.py entries I need (I can't edit it): bucket name, BigQuery dataset, the four table names, per-API timeouts, NEWSAPI_KEY, CRUNCHBASE_KEY, and cache TTL for NewsAPI. Can you add these in Phase 0, and I'll send the exact names?

4. Errors: I'd like typed exceptions for harvest failure and storage write failure in errors.py.

5. Function signatures I'll provide for you to call (please confirm or change):
- gcp/storage.py: write_json(session_id, name, data), read_json(session_id, name), read_all_agents(session_id)
- context/harvester.py: harvest(region, industry, session_id) -> ContextPackage, plus which sources succeeded
- gcp/bigquery.py: one log function per table (brd_runs, harvest logs, evaluator_scores, heatmap), fire-and-forget
- output/pdf_export.py: generate_pdfs(merged_brd) for the three views, so you can add GET /brd/{id}/pdf?view=

I'll push storage.py first since your swarm needs it at the start of Phase 2.

6. Please also check what Gemini model IDs resolve on your keys. The docs say 1.5, which may be retired, and my grounding calls depend on it. And if we can call through Vertex instead of AI Studio keys, that would also cover the Vertex requirement in the problem statement.

Since we push straight to main, I'll only touch my own folders. If you want a change in your files, tell me and I'll send the exact lines. Can you reply with answers to 1, 3 and 5 first?
```

---

## 4. You shared the live repo: what had changed

GitHub blocked the commit history, so I compared the live `README.md` and `TECHSTACK.md` against the zip.

**Fixed in `TECHSTACK.md`**
- Vertex AI is now the Gemini access path, using a service account with Application Default Credentials.
- The 20-key rotation is gone.
- Post-merge Gemini calls are now counted.
- Model names changed (the live file says 2.0 Flash plus 1.5 Pro).
- GCS blob names now use `output_investor/technical/regulatory.pdf`.

**Still open**
- `README.md` still had the old stack (Gemini 1.5 Flash and Pro, no Vertex path).
- Gemini 1.5 Pro is probably retired on Vertex; Zahid should confirm which model IDs resolve.
- `ARCHITECTURE.md` may still have the key-rotation section.
- The README says "Manipal Hackathon 2026"; check that it's correct.
- Only 2 commits at that point and no `backend/` or `frontend/` folders yet.

---

## 5. Phase 0 starter files (first version, before you asked for steps)

I wrote four files: `gcp/schema.sql`, `scripts/setup_gcp.sh`, `scripts/check_keys.py` and `gcp/storage.py`. Then you asked for one step at a time, so we switched approach (section 6).

---

## 6. Your working rules for me, from here on

1. You created your own branch **`hp/backend`** and push everything there.
2. **One step at a time:** one file per step, ready to commit; no giant dumps.
3. **You use Google Antigravity,** so I give you a **prompt to paste into the agent**, not raw code to paste by hand.

---

## 7. Step-by-step build

### Step 1: Get onto the branch

```
git fetch origin
git checkout hp/backend
git pull origin hp/backend
git status
ls
```

You then uploaded `Prism-Hp-backend.zip`. Zahid had pushed a backend skeleton with empty stub files for your area. Notes from inspecting it:
- Zahid's stubs use `write_json(session_id, filename, data) -> str`, `read_json(session_id, filename)` and `write_pdf(session_id, filename, pdf_bytes, view) -> str`, so we kept those exact signatures.
- Config names: `settings.GCS_BUCKET_NAME` (default `prism-sessions`, not `prism-outputs`), `settings.BIGQUERY_DATASET`, `settings.GCP_PROJECT_ID`, `settings.HARVESTER_TIMEOUT_SECONDS`, `NEWSAPI_KEY`, `CRUNCHBASE_KEY`.
- `bigquery.py` stubs were `log_run_to_bigquery` and `log_context_harvest`.

### Step 2: `backend/gcp/storage.py` (Antigravity prompt)

```
Implement backend/gcp/storage.py. Replace the NotImplementedError stubs. Do not touch any other file.

Keep these exact function signatures (other modules call them):
- async def write_json(session_id: str, filename: str, data: dict) -> str
- async def read_json(session_id: str, filename: str) -> dict | None
- async def write_pdf(session_id: str, filename: str, pdf_bytes: bytes, view: str) -> str

Requirements:
1. Use google-cloud-storage with Application Default Credentials. Create the client lazily once (module-level), using settings.GCP_PROJECT_ID and the bucket settings.GCS_BUCKET_NAME from backend.config. No hardcoded names.
2. google-cloud-storage is synchronous, so wrap every blocking call in asyncio.to_thread.
3. Security: the object path must be built from the session ID only. Validate session_id with uuid.UUID and always lowercase it. Reject anything else by raising StorageError (from backend.errors) with a generic message and the reason in detail.
4. filename for JSON must be in an allowlist: intake_package, agent_vc, agent_lean, agent_cto, agent_ux, agent_regulator, agent_adversarial, score_matrix, merged_brd, heatmap, investor_readiness. Accept it with or without the .json suffix. Path is {session_id}/{name}.json.
5. For write_pdf, view must be one of investor, technical, regulatory. Path is {session_id}/output_{view}.pdf. The filename argument is ignored.
6. JSON writes use content_type="application/json" and PDFs use "application/pdf". After every write, confirm with blob.exists() and raise StorageError if it is not confirmed. Writes return the gs://bucket/path string.
7. read_json must check blob.exists() first and return None if the blob is missing.
8. Any unexpected exception from the GCS library must be re-raised as StorageError with a generic message. Put the exception type name in detail only. Never log or include credentials.
9. Add type hints everywhere. No comments except a one-line module docstring.

Then write a pytest test file backend/tests/test_storage.py using unittest.mock to fake the bucket. Cover: successful write and read, read of a missing blob returns None, an invalid session id is rejected, an unknown filename is rejected, and path-traversal strings are rejected. Run the tests and show me the result.
```

Commit:

```
git add backend/gcp/storage.py backend/tests/test_storage.py
git commit -m "feat(gcp): implement GCS storage helpers"
git push origin hp/backend
```

### Step 3: `backend/gcp/schema.sql` (Antigravity prompt)

```
Create backend/gcp/schema.sql. Do not modify any other file.

Read the BigQuery section of SCHEMA.md in the repo root and write the CREATE TABLE statements for all four tables in the dataset prism_data:
- brd_runs
- context_harvest_logs
- evaluator_scores
- divergence_heatmap_data

Rules:
1. Start with: CREATE SCHEMA IF NOT EXISTS prism_data;
2. Use CREATE TABLE IF NOT EXISTS prism_data.<table> for every table.
3. Use exactly the columns, types and required/optional status from SCHEMA.md. Do not invent, rename or drop columns. REQUIRED columns get NOT NULL. Use ARRAY<STRING> for list-of-string columns.
4. Where SCHEMA.md gives a default (for example created_at, cached, pivot_triggered, schema_version), add it with DEFAULT.
5. Partitioning and clustering:
   - brd_runs: PARTITION BY DATE(created_at), CLUSTER BY region, industry, status
   - context_harvest_logs: PARTITION BY DATE(harvested_at), CLUSTER BY source, region
   - evaluator_scores: PARTITION BY DATE(evaluated_at), CLUSTER BY session_id, agent_name
   - divergence_heatmap_data: no partitioning
6. Plain SQL only, no comments, standard BigQuery syntax.

When finished, list any place where SCHEMA.md was ambiguous or contradicted itself, and tell me what you chose.
```

**Agent's reported ambiguities, and my verdict (all three correct):**
1. `brd_runs.session_id` is described as partition key but the footer says partition by `created_at`. BigQuery allows one partition key, so `PARTITION BY DATE(created_at)` is right.
2. `input_modalities` as `ARRAY<STRING>` is the right way to express a repeated string.
3. `calculated_at` with no default is right; the pipeline sets it when computing the heatmap.

Commit:

```
git add backend/gcp/schema.sql
git commit -m "feat(gcp): add BigQuery table definitions"
git push origin hp/backend
```

### Step 4: `backend/scripts/check_keys.py` (Antigravity prompt)

```
Create backend/scripts/check_keys.py. Do not modify any other file. Create backend/scripts/ if it doesn't exist.

Purpose: a standalone script I run manually to verify every external service I own is reachable. Read the settings object in backend/config.py and the existing requirements.txt first. Use the existing setting names and the HTTP and Google libraries already in requirements.txt. Do not add dependencies without telling me.

Checks, each run independently so one failure never stops the rest (10 second timeout each):
1. NewsAPI: GET https://newsapi.org/v2/top-headlines with country=in and pageSize=1. Send the key in the X-Api-Key header, never in the URL. Print the status code and the x-ratelimit-remaining header if present.
2. World Bank: for country IN, fetch the latest value (mrnev=1, format=json) of these four indicators: NY.GDP.MKTP.CD, FP.CPI.TOTL.ZG, BX.KLT.DINV.WD.GD.ZS, IC.BUS.EASE.XQ. Report per indicator whether a non-null value came back and which year. No key needed.
3. Crunchbase: one minimal authenticated request to the v4 API using the key from settings, in the X-cb-user-key header. Print the status code. If it is 401 or 403, print: "No usable access - use the static fallback".
4. Cloud Storage: confirm the bucket named in settings exists.
5. BigQuery: confirm the dataset in settings exists and contains these tables: brd_runs, context_harvest_logs, evaluator_scores, divergence_heatmap_data.
6. Vertex AI: send one tiny prompt ("Reply with the single word: pong") using the same project, location and model that the rest of the backend is configured to use, and print the latency.

Output rules:
- One line per check: [OK] or [FAIL], the check name, and the status code or exception type name. Never print API keys, tokens, request headers, or full exception messages.
- If a key is missing from settings, print [FAIL] with "key not set" and continue.
- At the end, print "X/Y passed" and exit with code 1 if anything failed.
- Type hints, no comments except a module docstring. Run it with: python -m backend.scripts.check_keys
```

You reported it done and pushed (commit `40b945b`). One thing I flagged: you wrote the branch as `origin/Hp/backend` with a capital H. You confirmed it was pushed to the right branch.

### Step 5: Run the script. First result

```
[FAIL] NewsAPI - key not set
[FAIL] World Bank - NY.GDP.MKTP.CD: HTTP 502, FP.CPI.TOTL.ZG: HTTP 502, BX.KLT.DINV.WD.GD.ZS: HTTP 502, IC.BUS.EASE.XQ: HTTP 502
[FAIL] Crunchbase - key not set
[FAIL] Cloud Storage - DefaultCredentialsError
[FAIL] BigQuery - DefaultCredentialsError
[FAIL] Vertex AI - DefaultCredentialsError
0/6 passed
```

What it meant:

| Result | Meaning |
|---|---|
| NewsAPI and Crunchbase "key not set" | Keys aren't in `.env` yet |
| Cloud Storage, BigQuery, Vertex "DefaultCredentialsError" | Not logged in to Google Cloud yet |
| World Bank 502 | A temporary server-side error; re-run later |

`gcloud` wasn't installed (not recognised in PATH).

### Step 6: Install gcloud and log in (Antigravity prompt)

```
I need Google Cloud authentication working on this Windows machine so the backend can reach Cloud Storage, BigQuery and Vertex AI. Do not modify any file in the repo. Do not create or download any service account key files.

1. Check whether gcloud is installed: run `gcloud --version`. If it is not recognised, install the Google Cloud SDK for Windows (use `winget install Google.CloudSDK`, or the official installer from cloud.google.com/sdk/docs/install if winget is unavailable). Then refresh PATH for this session, or tell me clearly if I need to restart the terminal, and confirm with `gcloud --version`.

2. Run `gcloud auth application-default login`. It will open a browser window, so tell me when it does and wait for me to finish signing in.

3. Ask me for the GCP project ID, then run `gcloud config set project <ID>` and `gcloud auth application-default set-quota-project <ID>`.

4. Run `gcloud auth application-default print-access-token > NUL` (do not print the token) to confirm credentials work, and report only success or failure.

5. Run `python -m backend.scripts.check_keys` and show me the full output.

Never print tokens, keys or credential file contents. If any step fails, show the error and stop instead of trying workarounds.
```

Result: the SDK installed (Google Cloud SDK 587.0.0). The agent opened a browser login that you couldn't see, and it asked for the GCP project ID.

### Step 7: World Bank client (Antigravity prompt, sent while waiting for the project ID)

I checked first: `backend/context/worldbank.py` existed as a stub with `async def fetch_worldbank(region: str) -> MarketData`, and `MarketData` has `gdp_per_capita_usd`, `ease_of_doing_business_rank`, `inflation_rate_pct` and `source_year`.

```
Implement backend/context/worldbank.py. Replace the NotImplementedError. Modify only this file, plus add backend/tests/test_worldbank.py.

Keep the signature: async def fetch_worldbank(region: str) -> MarketData. MarketData is in backend/models/context.py. Do not edit that model.

Behaviour:
1. Use httpx.AsyncClient (already in requirements.txt; check first). Timeout comes from settings.HARVESTER_TIMEOUT_SECONDS in backend.config. No hardcoded timeout values.
2. Map the region string to a World Bank country code with a small module-level dict (case-insensitive, trimmed). Include India (IN), United States (US), United Kingdom (GB), Singapore (SG), United Arab Emirates (AE) and Germany (DE). If the region is not in the dict, return an empty MarketData() without making any request.
3. Fetch the latest non-null value for each indicator, in parallel with asyncio.gather. URL pattern: https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&mrnev=1
   - NY.GDP.PCAP.CD -> gdp_per_capita_usd (float)
   - FP.CPI.TOTL.ZG -> inflation_rate_pct (float)
   - IC.BUS.EASE.XQ -> ease_of_doing_business_rank (int). This series was discontinued, so its latest year may be old. If there is no value, leave the field None.
4. source_year is the most recent year among the indicators that returned a value, or None.
5. This function must never raise. Any timeout, HTTP error, bad JSON or unexpected response shape for an indicator leaves that field None. One indicator failing must not affect the others. A 502 or 503 should be retried once after a short pause before giving up.
6. Never include the region text in the URL unless it was mapped to a code from the dict (no user input reaches the request).
7. Type hints, one-line module docstring, no other comments.

Tests (pytest + mocking httpx, no real network): all indicators succeed; one indicator returns 502 then recovers on retry; one indicator fails permanently while the others still fill in; unknown region returns empty MarketData and makes zero requests; null values in the response give None fields.

Run the tests and show me the result.
```

Commit (once its tests pass):

```
git add backend/context/worldbank.py backend/tests/test_worldbank.py
git commit -m "feat(context): implement World Bank client"
git push origin hp/backend
```

**Status:** you said you'd send this to Antigravity; I haven't seen its result yet.

---

## 8. GCP project: where we are

- The browser login never opened. Fallback for the sign-in: `gcloud auth login --no-launch-browser` (and the same flag for `application-default login`), then paste the verification code back.
- You asked Zahid for the project ID. His reply (which looked AI-generated) said no project exists yet: the repo only has the placeholder `your-gcp-project-id`.
- So someone has to create the project. You can do it yourself, but the team must all end up on **one** project, because Zahid's backend writes to the same bucket and BigQuery tables that your code sets up.

### Setup prompt for Antigravity (create project, bucket, tables, `.env`)

```
Set up a Google Cloud project for the PRISM backend on this Windows machine. Do not modify any file in the repo and do not create service account key files. Never print tokens or keys.

1. Authenticate in a way that works without a visible browser: run `gcloud auth login --no-launch-browser`, show me the URL it prints, and wait for me to paste back the verification code. Then do the same with `gcloud auth application-default login --no-launch-browser`.

2. Create a new project with a globally unique ID of the form prism-hp-<5 random digits> and the name "PRISM". Run `gcloud projects create`, then `gcloud config set project <ID>` and `gcloud auth application-default set-quota-project <ID>`. Tell me the final project ID clearly.

3. Run `gcloud billing accounts list`. Show me the result and ask me whether to link a billing account. Do NOT link billing without my explicit confirmation. Vertex AI needs billing enabled.

4. After I confirm, link billing, then enable these APIs: aiplatform.googleapis.com, storage.googleapis.com, bigquery.googleapis.com.

5. Create the Cloud Storage bucket with the name settings.GCS_BUCKET_NAME in backend/config.py (read the value, do not edit the file), in region us-central1, with uniform bucket-level access. Create the BigQuery dataset named settings.BIGQUERY_DATASET in the same region, then run backend/gcp/schema.sql against it with `bq query --use_legacy_sql=false`.

6. Create backend/.env from backend/.env.example if it doesn't exist, and set GCP_PROJECT_ID to the new project ID and GCP_REGION to us-central1. Make sure backend/.env is listed in .gitignore. Tell me if it was not.

7. Run `python -m backend.scripts.check_keys` and show me the full output.

If any step fails, show the error and stop instead of trying workarounds.
```

### Message I suggested sending Zahid

```
Zahid, the repo has no real GCP project yet, just a placeholder in config. Do we have one with credits already? If not, I'll create it now on my account (prism-hp-xxxxx) and add you as an owner so we all use the same project. Reply in the next 10 min or I'll go ahead.
```

### You said: "we only have to use free resources, Google ones"

What I found from Google's own free-trial and free-tier pages:
- New users get a **90-day trial with $300 in credit** and are **not billed during it**. Signup needs a credit card or other payment method, which is used to verify identity.
- The **always-free tier** includes 5 GB of Cloud Storage (certain US regions only; `us-central1` is one) and 1 TiB of BigQuery queries per month. It carries on after the trial ends, with no charge until you manually upgrade.
- **Vertex AI (Gemini) is not covered by an always-free tier** as far as I could confirm. It draws on the $300 trial credit, which is far more than a hackathon demo needs. Check the Vertex pricing page before heavy rehearsals.

Warnings:
- The trial may not be offered if the Google account has used Google Cloud billing before. If so, fall back to the free Gemini API (AI Studio) route.
- Never click "upgrade" or "activate full account"; that is what starts real charges.

Safety-net prompt to run after setup:

```
Create a budget alert on the PRISM project's billing account for 5 USD with alert thresholds at 50%, 90% and 100%, using `gcloud billing budgets create`. Show me the result. Do not change any other billing settings and do not upgrade the account.
```

I also asked whether the Google account is personal or a college one, since a college account may restrict project creation.

---

## 9. Where things stand and what's next

**Done and pushed to `hp/backend`**
- Step 2: `gcp/storage.py` + tests
- Step 3: `gcp/schema.sql`
- Step 4: `scripts/check_keys.py`

**In progress**
- Step 7: World Bank client (sent to Antigravity; result not yet seen)
- GCP project: not created yet; waiting on the Zahid decision, or run the setup prompt above on your own account

**Next steps, in order**
1. Finish the GCP setup (project, billing on the free trial, bucket, tables, `.env`).
2. Re-run `python -m backend.scripts.check_keys` and paste the output.
3. Put `NEWSAPI_KEY` and `CRUNCHBASE_KEY` into `backend/.env`.
4. Decide Crunchbase (live or static fallback) from the check result.
5. Step 8 onwards: NewsAPI client, Crunchbase client, then government data, grounding, `harvester.py`, `bigquery.py` logging, then the output layer (Phase 3).

**Open items to raise with the team**
- Confirm which Gemini model IDs actually resolve on Vertex (Zahid).
- `.env.example` names the bucket `prism-sessions`; docs say `prism-outputs`. Pick one and create the bucket with that name.
- The README may still say "Manipal Hackathon 2026" and the old Gemini 1.5 stack; fix before the PPT.
- World Bank's `IC.BUS.EASE.XQ` series was discontinued, so expect an old year or an empty value.
