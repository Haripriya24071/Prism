"""backend/gcp/bigquery.py — BigQuery fire-and-forget asynchronous logging helpers."""

import asyncio
from datetime import datetime
import logging
from typing import Any, Optional
import uuid
from google.cloud import bigquery
from backend.config import settings

logger = logging.getLogger(__name__)

_bq_client: Optional[bigquery.Client] = None


def _get_bigquery_client() -> Optional[bigquery.Client]:
    """Lazily initialize and return the BigQuery client."""
    global _bq_client
    if _bq_client is None:
        try:
            _bq_client = bigquery.Client(project=settings.GCP_PROJECT_ID)
        except Exception as e:
            logger.warning("bigquery_client_init_failed: %s", type(e).__name__)
            return None
    return _bq_client


def _sync_insert_rows(table_name: str, rows: list[dict[str, Any]]) -> None:
    """Synchronous insertion of rows to a BigQuery table in dataset."""
    client = _get_bigquery_client()
    if client is None or not rows:
        return
    dataset_name = settings.BIGQUERY_DATASET
    table_ref = f"{settings.GCP_PROJECT_ID}.{dataset_name}.{table_name}"
    try:
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.warning("bigquery_insert_errors: table=%s, errors=%s", table_name, errors)
    except Exception as e:
        logger.warning("bigquery_insert_failed: table=%s, error=%s", table_name, type(e).__name__)


async def log_run_to_bigquery(
    session_id: str,
    score: int | float,
    duration_ms: int,
    agent_count: int,
    region: str = "IN",
    industry: str = "General",
    status: str = "completed",
    error_message: Optional[str] = None,
    intake_summary: str = "PRISM BRD Run",
) -> None:
    """Log BRD session run record into BigQuery brd_runs table (fire-and-forget)."""
    row = {
        "session_id": str(session_id).lower(),
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat() if status == "completed" else None,
        "user_anonymous_id": "anonymous_user",
        "intake_summary": intake_summary,
        "region": region,
        "industry": industry,
        "stage": "idea",
        "status": status,
        "error_message": error_message,
        "input_modalities": ["text"],
        "gcs_session_prefix": f"{session_id}/",
        "investor_readiness_score": float(score) if score is not None else None,
        "pivot_triggered": False,
        "schema_version": 1,
    }
    try:
        await asyncio.to_thread(_sync_insert_rows, "brd_runs", [row])
    except Exception as e:
        logger.warning("log_run_to_bigquery_failed: %s", type(e).__name__)


async def log_context_harvest(
    session_id: str,
    sources: list[str],
    duration_ms: int,
    region: str = "IN",
    industry: str = "General",
) -> None:
    """Log harvester events into BigQuery context_harvest_logs table (fire-and-forget)."""
    rows = []
    now = datetime.utcnow().isoformat()
    for src in sources:
        rows.append(
            {
                "harvest_id": str(uuid.uuid4()),
                "session_id": str(session_id).lower(),
                "harvested_at": now,
                "source": src,
                "region": region,
                "industry": industry,
                "request_url": f"https://api.{src}.internal",
                "response_status_code": 200,
                "response_item_count": 1,
                "latency_ms": int(duration_ms),
                "cached": False,
                "error_detail": None,
            }
        )
    if rows:
        try:
            await asyncio.to_thread(_sync_insert_rows, "context_harvest_logs", rows)
        except Exception as e:
            logger.warning("log_context_harvest_failed: %s", type(e).__name__)
