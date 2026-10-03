# PRISM — Schema Reference

---

## BigQuery Dataset: `prism_data`

---

### Table: `brd_runs`

Primary record for every BRD generation session.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `session_id` | STRING | REQUIRED | UUID v4. Server-generated. Primary key. Partition key. |
| `created_at` | TIMESTAMP | REQUIRED | UTC. Default: `CURRENT_TIMESTAMP()` |
| `completed_at` | TIMESTAMP | NULLABLE | UTC. Populated when status = `complete` |
| `user_anonymous_id` | STRING | NULLABLE | Hashed browser fingerprint. No PII. Max 64 chars. |
| `intake_summary` | STRING | REQUIRED | JSON string of extracted intake data. Max 10,000 chars. |
| `region` | STRING | REQUIRED | ISO 3166-1 alpha-2. e.g. `IN`, `US`, `NG` |
| `industry` | STRING | REQUIRED | Free-text industry tag. Max 100 chars. |
| `stage` | STRING | NULLABLE | ENUM: `idea` / `prototype` / `mvp` / `growth` |
| `status` | STRING | REQUIRED | ENUM: `intake` / `harvesting` / `swarm_running` / `evaluating` / `merging` / `complete` / `failed` |
| `error_message` | STRING | NULLABLE | Last error if status = `failed`. Max 2,000 chars. |
| `input_modalities` | STRING | REPEATED | ENUM values: `text` / `voice` / `image` / `document` |
| `gcs_session_prefix` | STRING | REQUIRED | e.g. `gs://prism-outputs/{session_id}/` |
| `investor_readiness_score` | FLOAT64 | NULLABLE | 0–100.0. Populated on completion. |
| `pivot_triggered` | BOOL | REQUIRED | True if investor score < 60 and pivot suggester fired. Default: false. |
| `schema_version` | INT64 | REQUIRED | Default: `1`. Increment on schema changes. |

**Partitioning:** `created_at` (DATE), daily.
**Clustering:** `region`, `industry`, `status`.

---

### Table: `context_harvest_logs`

One row per external API call during context harvesting.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `harvest_id` | STRING | REQUIRED | UUID v4. Primary key. |
| `session_id` | STRING | REQUIRED | FK → `brd_runs.session_id` |
| `harvested_at` | TIMESTAMP | REQUIRED | UTC. Default: `CURRENT_TIMESTAMP()` |
| `source` | STRING | REQUIRED | ENUM: `newsapi` / `worldbank` / `crunchbase` / `govt_open_data` / `gemini_grounding` |
| `region` | STRING | REQUIRED | ISO 3166-1 alpha-2. |
| `industry` | STRING | NULLABLE | Industry tag passed to this source. |
| `request_url` | STRING | REQUIRED | Full URL called. Max 2,000 chars. |
| `response_status_code` | INT64 | REQUIRED | HTTP response code. |
| `response_item_count` | INT64 | NULLABLE | Number of items returned. |
| `latency_ms` | INT64 | REQUIRED | Round-trip latency in milliseconds. |
| `cached` | BOOL | REQUIRED | Was result served from cache? Default: false. |
| `error_detail` | STRING | NULLABLE | Error message if status >= 400. |

**Partitioning:** `harvested_at` (DATE).
**Clustering:** `source`, `region`.

---

### Table: `evaluator_scores`

One row per agent × section × criterion scoring result.

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `score_id` | STRING | REQUIRED | UUID v4. Primary key. |
| `session_id` | STRING | REQUIRED | FK → `brd_runs.session_id` |
| `agent_name` | STRING | REQUIRED | ENUM: `vc` / `lean` / `cto` / `ux` / `regulator` / `adversarial` |
| `section_name` | STRING | REQUIRED | ENUM: `problem_statement` / `functional_requirements` / `technical_requirements` / `risk_register` / `timeline_milestones` |
| `criterion` | STRING | REQUIRED | ENUM: `feasibility` / `market_timing` / `regulatory_safety` / `user_adoption` / `competitive_moat` |
| `score` | FLOAT64 | REQUIRED | 0.0–100.0 |
| `citation` | STRING | NULLABLE | One-line data citation. Max 500 chars. |
| `evaluated_at` | TIMESTAMP | REQUIRED | UTC. Default: `CURRENT_TIMESTAMP()` |

**Partitioning:** `evaluated_at` (DATE).
**Clustering:** `session_id`, `agent_name`.

---

### Table: `divergence_heatmap_data`

| Column | Type | Mode | Description |
|--------|------|------|-------------|
| `heatmap_id` | STRING | REQUIRED | UUID v4. Primary key. |
| `session_id` | STRING | REQUIRED | FK → `brd_runs.session_id` |
| `section_name` | STRING | REQUIRED | Same ENUM as `evaluator_scores.section_name` |
| `agreement_score` | FLOAT64 | REQUIRED | 0.0–100.0. Higher = more agreement = lower risk. |
| `std_deviation` | FLOAT64 | REQUIRED | Raw std dev of 6 agent scores for this section. |
| `risk_level` | STRING | REQUIRED | ENUM: `low` (>70) / `medium` (40–70) / `high` (<40) |
| `min_score` | FLOAT64 | REQUIRED | Lowest agent score for this section. |
| `max_score` | FLOAT64 | REQUIRED | Highest agent score for this section. |
| `dominant_agent` | STRING | REQUIRED | Agent with highest score on this section. |
| `calculated_at` | TIMESTAMP | REQUIRED | UTC. |

---

## GCS Blob Structure

**Bucket:** `prism-outputs`
**Access:** Uniform Bucket-Level Access — IAM only, no ACLs.

```
prism-outputs/
└── {session_id}/                        ← UUID v4, always lowercase
    ├── intake_package.json              ← Full intake: conversation, extracted fields, context package
    ├── agent_vc.json                    ← Raw BRD from VC agent
    ├── agent_lean.json                  ← Raw BRD from Lean Founder agent
    ├── agent_cto.json                   ← Raw BRD from CTO agent
    ├── agent_ux.json                    ← Raw BRD from UX Researcher agent
    ├── agent_regulator.json             ← Raw BRD from Regulator agent
    ├── agent_adversarial.json           ← Raw BRD from Adversarial agent
    ├── score_matrix.json                ← Full evaluator output: all scores + citations
    ├── merged_brd.json                  ← Final merged BRD with lineage tags
    ├── heatmap.json                     ← Agreement scores + risk levels per section
    ├── investor_readiness.json          ← Score, gaps, pivot suggestions (if triggered)
    ├── output_investor.pdf              ← Investor-view PDF
    ├── output_technical.pdf             ← Technical-team PDF
    └── output_regulatory.pdf           ← Regulatory/compliance PDF
```

---

## JSON Blob Schemas

### `intake_package.json`

```json
{
  "session_id": "string (uuid4)",
  "created_at": "string (ISO 8601 UTC)",
  "conversation_turns": [
    { "role": "user|assistant", "content": "string" }
  ],
  "extracted": {
    "business_idea": "string",
    "region": "string (ISO 3166-1 alpha-2)",
    "industry": "string",
    "stage": "idea|prototype|mvp|growth",
    "budget_range": "string|null",
    "constraints": ["string"]
  },
  "file_contexts": {
    "image_analyses": ["string (Gemini Vision output per image)"],
    "document_summaries": ["string (extracted text per doc)"]
  },
  "context_package": {
    "news": [{ "headline": "string", "date": "string", "source": "string", "url": "string" }],
    "market": {
      "gdp_usd": "number",
      "ease_of_business_rank": "number",
      "inflation_pct": "number",
      "fdi_inflow_usd": "number"
    },
    "competitors": [{ "name": "string", "funding": "string", "stage": "string", "founded": "string" }],
    "regulatory": ["string"],
    "cultural": "string"
  }
}
```

### `merged_brd.json`

```json
{
  "session_id": "string",
  "generated_at": "string (ISO 8601 UTC)",
  "sections": {
    "problem_statement": {
      "content": "string",
      "source_agent": "vc|lean|cto|ux|regulator|adversarial",
      "agent_score": "number (0-100)",
      "data_citations": ["string"],
      "confidence_score": "number (0-100)",
      "assumptions": [
        {
          "text": "string",
          "confidence": "number (0-100)",
          "evidence": "string",
          "action": "string"
        }
      ],
      "dissenting_agents": [{ "agent": "string", "key_disagreement": "string" }]
    },
    "functional_requirements": { "...same shape..." },
    "technical_requirements": { "...same shape..." },
    "risk_register": {
      "...same shape...",
      "failure_modes": [
        {
          "title": "string",
          "probability_pct": "number",
          "description": "string",
          "mitigation": "string"
        }
      ]
    },
    "timeline_milestones": { "...same shape..." }
  },
  "investor_readiness_score": "number (0-100)",
  "investor_readiness_gaps": ["string"],
  "heatmap_summary": {
    "highest_risk_section": "string",
    "lowest_risk_section": "string"
  }
}
```

### `investor_readiness.json`

```json
{
  "session_id": "string",
  "score": "number (0-100)",
  "breakdown": {
    "feasibility": "number",
    "market_timing": "number",
    "regulatory_safety": "number",
    "user_adoption": "number",
    "competitive_moat": "number"
  },
  "gaps": ["string"],
  "pivot_triggered": "boolean",
  "pivot_suggestions": [
    {
      "title": "string",
      "description": "string",
      "projected_score": "number",
      "key_changes": ["string"]
    }
  ]
}
```

---

## Pydantic Models (Backend)

Key models in `backend/models/`:

```python
# models/intake.py
class ChatRequest(BaseModel):
    session_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
    content: str = Field(..., min_length=1, max_length=5000)
    role: Literal["user"]

class ExtractedIntake(BaseModel):
    business_idea: str
    region: str = Field(..., pattern=r'^[A-Z]{2}$')
    industry: str = Field(..., max_length=100)
    stage: Literal["idea", "prototype", "mvp", "growth"] | None = None
    budget_range: str | None = None
    constraints: list[str] = []

# models/brd.py
class LineageTag(BaseModel):
    source_agent: Literal["vc", "lean", "cto", "ux", "regulator", "adversarial"]
    agent_score: float = Field(..., ge=0, le=100)
    data_citations: list[str]
    confidence_score: float = Field(..., ge=0, le=100)

class BRDSection(BaseModel):
    content: str
    lineage: LineageTag
    assumptions: list[AssumptionFlag] = []
    dissenting_agents: list[DissentNote] = []

# models/output.py
class PivotSuggestion(BaseModel):
    title: str
    description: str
    projected_score: float = Field(..., ge=0, le=100)
    key_changes: list[str]

class InvestorReadiness(BaseModel):
    score: float = Field(..., ge=0, le=100)
    breakdown: dict[str, float]
    gaps: list[str]
    pivot_triggered: bool
    pivot_suggestions: list[PivotSuggestion] = []
```
