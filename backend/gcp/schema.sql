CREATE SCHEMA IF NOT EXISTS prism_data;

CREATE TABLE IF NOT EXISTS prism_data.brd_runs (
  session_id STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  completed_at TIMESTAMP,
  user_anonymous_id STRING,
  intake_summary STRING NOT NULL,
  region STRING NOT NULL,
  industry STRING NOT NULL,
  stage STRING,
  status STRING NOT NULL,
  error_message STRING,
  input_modalities ARRAY<STRING>,
  gcs_session_prefix STRING NOT NULL,
  investor_readiness_score FLOAT64,
  pivot_triggered BOOL NOT NULL DEFAULT FALSE,
  schema_version INT64 NOT NULL DEFAULT 1
)
PARTITION BY DATE(created_at)
CLUSTER BY region, industry, status;

CREATE TABLE IF NOT EXISTS prism_data.context_harvest_logs (
  harvest_id STRING NOT NULL,
  session_id STRING NOT NULL,
  harvested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  source STRING NOT NULL,
  region STRING NOT NULL,
  industry STRING,
  request_url STRING NOT NULL,
  response_status_code INT64 NOT NULL,
  response_item_count INT64,
  latency_ms INT64 NOT NULL,
  cached BOOL NOT NULL DEFAULT FALSE,
  error_detail STRING
)
PARTITION BY DATE(harvested_at)
CLUSTER BY source, region;

CREATE TABLE IF NOT EXISTS prism_data.evaluator_scores (
  score_id STRING NOT NULL,
  session_id STRING NOT NULL,
  agent_name STRING NOT NULL,
  section_name STRING NOT NULL,
  criterion STRING NOT NULL,
  score FLOAT64 NOT NULL,
  citation STRING,
  evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(evaluated_at)
CLUSTER BY session_id, agent_name;

CREATE TABLE IF NOT EXISTS prism_data.divergence_heatmap_data (
  heatmap_id STRING NOT NULL,
  session_id STRING NOT NULL,
  section_name STRING NOT NULL,
  agreement_score FLOAT64 NOT NULL,
  std_deviation FLOAT64 NOT NULL,
  risk_level STRING NOT NULL,
  min_score FLOAT64 NOT NULL,
  max_score FLOAT64 NOT NULL,
  dominant_agent STRING NOT NULL,
  calculated_at TIMESTAMP NOT NULL
);
