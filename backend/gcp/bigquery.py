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


async def log_run_to_bigquery(session_id: str, score: int, duration_ms: int, agent_count: int) -> None:
    raise NotImplementedError("Stub for Commit 1")


async def log_context_harvest(session_id: str, sources: list[str], duration_ms: int) -> None:
    raise NotImplementedError("Stub for Commit 1")
