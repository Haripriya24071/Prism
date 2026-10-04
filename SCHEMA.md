# PRISM — Schema & Data Contract Reference

> **Version:** 2.0 (Production Verified) | **Team:** Swapnil Ghosh, Zahid, Haripriya, Ritika  
> **Governing Docs:** [ARCHITECTURE.md](ARCHITECTURE.md), [PRD.md](PRD.md), [RULES.md](RULES.md)

---

## 1. Google BigQuery Schema: Dataset `prism_data`

### 1.1 Table: `brd_runs`
Records audit metadata for every completed or attempted BRD generation run.

| Field Name | Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `session_id` | STRING | REQUIRED | Unique session identifier (UUID v4). |
| `score` | INTEGER | NULLABLE | Overall composite Investor Readiness Score (0-100). |
| `duration_ms`| INTEGER | NULLABLE | Total pipeline generation time in milliseconds. |
| `agent_count`| INTEGER | NULLABLE | Number of agents participating in the swarm (default: 6). |
| `created_at` | STRING | NULLABLE | ISO-8601 UTC timestamp of execution. |

---

### 1.2 Table: `context_harvest_logs`
Records external data ingestion calls and latency per session.

| Field Name | Type | Mode | Description |
| :--- | :--- | :--- | :--- |
| `session_id` | STRING | REQUIRED | Associated session identifier (UUID v4). |
| `sources_ok` | STRING | REPEATED | List of external sources that completed successfully (e.g. `newsapi`, `worldbank`). |
| `source_count`| INTEGER | NULLABLE | Total number of successful context sources. |
| `duration_ms`| INTEGER | NULLABLE | Wall-clock latency of parallel harvesting in milliseconds. |
| `created_at` | STRING | NULLABLE | ISO-8601 UTC timestamp of harvest completion. |

---

## 2. Google Cloud Storage Blob Hierarchy

All persistent artifacts are stored under the bucket `prism-outputs` (or local fallback `/tmp/prism-sessions/`) under the session's unique path prefix:

```text
prism-outputs/{session_id}/
├── intake_package.json          # Formatted intake payload + extraction
├── agent_vc.json               # Full 6-section BRD contribution from VC persona
├── agent_lean.json             # Full 6-section BRD contribution from Lean Founder
├── agent_cto.json              # Full 6-section BRD contribution from Enterprise CTO
├── agent_ux.json               # Full 6-section BRD contribution from UX Researcher
├── agent_regulator.json        # Full 6-section BRD contribution from Regulator
├── agent_adversarial.json      # Full 6-section BRD contribution from Adversarial
├── score_matrix.json           # Impartial rubric scores across 5 criteria
├── merged_brd.json             # Synthesised master BRD with section lineage tags
├── heatmap.json                # Standard deviation divergence scores (0-100)
├── investor_readiness.json     # Final score, confidence rating, and gap flags
├── output_investor.pdf         # Compiled PDF tailored for venture investors
├── output_technical.pdf        # Compiled PDF tailored for engineering leads
└── output_regulatory.pdf       # Compiled PDF tailored for compliance officers
```

---

## 3. Pydantic Model Data Contracts

### 3.1 `IntakePackage` (`backend/models/intake.py`)
```python
class IntakeExtraction(BaseModel):
    raw_idea: str
    region: Optional[str] = None          # ISO 3166-1 alpha-2 (e.g. 'US', 'IN')
    industry: Optional[str] = None        # e.g. 'FinTech', 'Developer Tools'
    stage: Optional[str] = None           # 'idea' | 'prototype' | 'mvp' | 'growth'
    budget_range: Optional[str] = None    # e.g. '$10K-$50K'
    success_definition: Optional[str] = None

class IntakePackage(BaseModel):
    session_id: str
    extraction: IntakeExtraction
    file_context: Optional[str] = None
    conversation_history: List[dict] = []
    created_at: datetime
```

### 3.2 `AgentOutput` (`backend/models/agents.py`)
```python
class AgentPersona(str, Enum):
    VC = "vc"
    LEAN = "lean"
    CTO = "cto"
    UX = "ux"
    REGULATOR = "regulator"
    ADVERSARIAL = "adversarial"

class AgentOutput(BaseModel):
    agent: AgentPersona
    brd_json: Dict[str, str]              # 6 keys: Executive Summary, Market Analysis, etc.
    raw_text: str
    completed_at: datetime
    duration_ms: int
    failed: bool = False
```

### 3.3 `MergedBRD` (`backend/models/brd.py`)
```python
class LineageTag(BaseModel):
    section: str
    author_persona: AgentPersona
    original_score: float
    data_citations: List[str]             # e.g. ['[SOURCE: worldbank]']

class MergedBRD(BaseModel):
    session_id: str
    sections: Dict[str, str]              # The 6 authoritative merged sections
    lineage: Dict[str, LineageTag]        # Traceability for every section
    assumptions: List[dict] = []          # Unstated assumptions challenged
    failure_modes: List[dict] = []        # Top failure vectors with mitigations
```

### 3.4 `HeatmapData` & `InvestorScore` (`backend/models/output.py`)
```python
class SectionDivergence(BaseModel):
    section: str
    divergence_score: float               # 0 (consensus) to 100 (contested debate)
    risk_level: str                       # 'low' | 'medium' | 'high'
    dissent_summary: str

class HeatmapData(BaseModel):
    session_id: str
    sections: List[SectionDivergence]

class InvestorScore(BaseModel):
    composite_score: int                  # 0 to 100
    readiness_band: str                   # 'High Confidence' | 'Needs Polish' | 'Pivot Advised'
    gap_flags: List[str]
    pivot_suggestions: Optional[List[dict]] = None
```
