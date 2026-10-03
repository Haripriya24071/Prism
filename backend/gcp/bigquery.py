"""backend/gcp/bigquery.py — BigQuery fire-and-forget logging helpers."""


async def log_run_to_bigquery(session_id: str, score: int, duration_ms: int, agent_count: int) -> None:
    raise NotImplementedError("Phase 10")


async def log_context_harvest(session_id: str, sources: list[str], duration_ms: int) -> None:
    raise NotImplementedError("Phase 10")
