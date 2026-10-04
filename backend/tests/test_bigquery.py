"""backend/tests/test_bigquery.py — Unit tests for BigQuery logging module."""

from unittest.mock import MagicMock, patch
import pytest
from backend.gcp import bigquery


@pytest.mark.asyncio
async def test_log_run_to_bigquery_success():
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = []

    with patch("backend.gcp.bigquery._get_bigquery_client", return_value=mock_client):
        await bigquery.log_run_to_bigquery(
            session_id="12345678-1234-5678-1234-567812345678",
            score=88,
            duration_ms=4500,
            agent_count=6,
        )

    mock_client.insert_rows_json.assert_called_once()
    args, kwargs = mock_client.insert_rows_json.call_args
    assert "brd_runs" in args[0]
    assert args[1][0]["investor_readiness_score"] == 88.0


@pytest.mark.asyncio
async def test_log_context_harvest_success():
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = []

    with patch("backend.gcp.bigquery._get_bigquery_client", return_value=mock_client):
        await bigquery.log_context_harvest(
            session_id="12345678-1234-5678-1234-567812345678",
            sources=["newsapi", "worldbank"],
            duration_ms=1200,
        )

    mock_client.insert_rows_json.assert_called_once()
    args, kwargs = mock_client.insert_rows_json.call_args
    assert "context_harvest_logs" in args[0]
    assert len(args[1]) == 2


@pytest.mark.asyncio
async def test_bigquery_handles_exceptions_gracefully():
    mock_client = MagicMock()
    mock_client.insert_rows_json.side_effect = RuntimeError("BigQuery down")

    with patch("backend.gcp.bigquery._get_bigquery_client", return_value=mock_client):
        # Should not raise exception
        await bigquery.log_run_to_bigquery(
            session_id="12345678-1234-5678-1234-567812345678",
            score=75,
            duration_ms=2000,
            agent_count=6,
        )
