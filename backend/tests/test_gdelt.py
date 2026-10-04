"""backend/tests/test_gdelt.py — Unit tests for GDELT political context harvester."""

import pytest
import httpx
from backend.context.gdelt import fetch_political_context


@pytest.mark.asyncio
async def test_fetch_political_context_success(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "articles": [
                    {
                        "title": "India introduces new fintech guidelines",
                        "url": "https://example.com/fintech",
                        "seendate": "20261001T120000Z",
                        "domain": "example.com",
                    }
                ]
            }

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    res = await fetch_political_context("IN", "Fintech")
    assert res.get("data_source") == "gdelt_project"
    assert res.get("country") == "India"
    assert len(res.get("political_events", [])) == 1
    assert res["political_events"][0]["title"] == "India introduces new fintech guidelines"


@pytest.mark.asyncio
async def test_fetch_political_context_empty_region():
    res = await fetch_political_context("", "Fintech")
    assert res == {}


@pytest.mark.asyncio
async def test_fetch_political_context_error_resilience(monkeypatch):
    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("Network error")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    res = await fetch_political_context("US", "Healthcare")
    assert res == {}
