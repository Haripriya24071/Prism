"""backend/tests/test_alphavantage.py — Unit tests for Alpha Vantage market sentiment harvester."""

import pytest
import httpx
from backend.context.alphavantage import fetch_market_sentiment


@pytest.mark.asyncio
async def test_fetch_market_sentiment_success(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "feed": [
                    {"title": "Markets rise", "overall_sentiment_score": 0.25},
                    {"title": "Tech booming", "overall_sentiment_score": 0.35},
                ]
            }

    async def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    res = await fetch_market_sentiment("IN", "test_key")
    assert res.get("data_source") == "alpha_vantage"
    assert res.get("market_mood") == "bullish"
    assert res.get("market_sentiment_score") == 0.3


@pytest.mark.asyncio
async def test_fetch_market_sentiment_missing_key():
    res = await fetch_market_sentiment("IN", "")
    assert res == {}


@pytest.mark.asyncio
async def test_fetch_market_sentiment_error_resilience(monkeypatch):
    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("Timeout")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    res = await fetch_market_sentiment("US", "key123")
    assert res == {}
