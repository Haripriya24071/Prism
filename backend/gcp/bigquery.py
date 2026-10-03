"""backend/gcp/bigquery.py — BigQuery fire-and-forget logging helpers."""

import asyncio
from datetime import datetime, timezone
from typing import Any
import structlog
from config import settings

logger = structlog.get_logger()


def _get_bq_client() -> Any:
    """Returns BigQuery client. Import here to avoid module-level auth errors in dev."""
    from google.cloud import bigquery
    return bigquery.Client(project=settings.gcp_project_id)


def _table_ref(table_name: str) -> str:
    """Format table reference as project.dataset.table_name."""
    return f"{settings.gcp_project_id}.{settings.bigquery_dataset}.{table_name}"


async def log_run_to_bigquery(
    session_id: str,
    score: int,
    duration_ms: int,
    agent_count: int,
) -> None:
    """
    Fire-and-forget BRD run log to BigQuery.
    Table: {project}.{dataset}.brd_runs
    Never raises — logs error and returns silently on any failure.
    """
    if not settings.bigquery_dataset or settings.env == "development":
        logger.debug("bq_logging_disabled", reason="dev_mode_or_no_dataset")
        return

    row = {
        "session_id": session_id,
        "score": score,
        "duration_ms": duration_ms,
        "agent_count": agent_count,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        def _insert() -> None:
            client = _get_bq_client()
            errors = client.insert_rows_json(_table_ref("brd_runs"), [row])
            if errors:
                logger.warning("bq_insert_errors", table="brd_runs", errors=len(errors))

        await asyncio.to_thread(_insert)
        logger.info("bq_run_logged", session_id=session_id, score=score, duration_ms=duration_ms)
    except Exception as e:
        logger.error("bq_run_log_failed", error_type=type(e).__name__)


async def log_context_harvest(session_id: str, sources: list[str], duration_ms: int) -> None:
    raise NotImplementedError("Stub for Commit 2")
