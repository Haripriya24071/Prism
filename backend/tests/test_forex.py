"""backend/tests/test_forex.py — Unit tests for zero-key foreign exchange harvester."""

import pytest
from backend.context.forex import fetch_forex_data


@pytest.mark.asyncio
async def test_fetch_forex_data_in():
    res = await fetch_forex_data("IN")
    assert isinstance(res, dict)
    assert res.get("local_currency") == "INR"
    assert res.get("currency_symbol") == "₹"
    assert res.get("exchange_rate_per_usd") > 50.0
    assert "forex_volatility_risk" in res


@pytest.mark.asyncio
async def test_fetch_forex_data_us():
    res = await fetch_forex_data("US")
    assert isinstance(res, dict)
    assert res.get("local_currency") == "USD"
    assert res.get("exchange_rate_per_usd") == 1.0


@pytest.mark.asyncio
async def test_fetch_forex_fallback(monkeypatch):
    import httpx

    async def mock_get(*args, **kwargs):
        raise httpx.RequestError("Network error")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    res = await fetch_forex_data("GB")
    assert isinstance(res, dict)
    assert res.get("local_currency") == "GBP"
    assert res.get("data_source") == "cached_baseline"
    assert res.get("exchange_rate_per_usd") == 0.78
