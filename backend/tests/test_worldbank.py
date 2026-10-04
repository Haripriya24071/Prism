"""backend/tests/test_worldbank.py — Unit tests for World Bank Open Data client."""

from typing import Any
import httpx
import pytest
from backend.context.worldbank import fetch_worldbank
from backend.models.context import MarketData


def _mock_response(status_code: int, json_data: Any = None) -> httpx.Response:
    request = httpx.Request("GET", "https://api.worldbank.org/v2/country/IN/indicator/TEST")
    return httpx.Response(status_code=status_code, json=json_data, request=request)


@pytest.mark.asyncio
async def test_all_indicators_succeed(monkeypatch):
    async def mock_get(self, url, *args, **kwargs):
        if "NY.GDP.PCAP.CD" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2023", "value": 2410.5}]])
        if "FP.CPI.TOTL.ZG" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2023", "value": 5.4}]])
        if "IC.BUS.EASE.XQ" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2019", "value": 63}]])
        return _mock_response(404)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_worldbank("India")

    assert isinstance(result, MarketData)
    assert result.gdp_per_capita_usd == 2410.5
    assert result.inflation_rate_pct == 5.4
    assert result.ease_of_doing_business_rank == 63
    assert result.source_year == 2023


@pytest.mark.asyncio
async def test_502_retry_success(monkeypatch):
    attempts: dict[str, int] = {"gdp": 0}

    async def mock_get(self, url, *args, **kwargs):
        if "NY.GDP.PCAP.CD" in str(url):
            attempts["gdp"] += 1
            if attempts["gdp"] == 1:
                return _mock_response(502)
            return _mock_response(200, [{"page": 1}, [{"date": "2022", "value": 2200.0}]])
        if "FP.CPI.TOTL.ZG" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2022", "value": 6.1}]])
        if "IC.BUS.EASE.XQ" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2019", "value": 65}]])
        return _mock_response(404)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_worldbank("IN")

    assert attempts["gdp"] == 2
    assert result.gdp_per_capita_usd == 2200.0
    assert result.inflation_rate_pct == 6.1
    assert result.ease_of_doing_business_rank == 65
    assert result.source_year == 2022


@pytest.mark.asyncio
async def test_partial_failure_leaves_none(monkeypatch):
    async def mock_get(self, url, *args, **kwargs):
        if "NY.GDP.PCAP.CD" in str(url):
            return _mock_response(500)
        if "FP.CPI.TOTL.ZG" in str(url):
            return _mock_response(200, [{"page": 1}, [{"date": "2023", "value": 4.8}]])
        if "IC.BUS.EASE.XQ" in str(url):
            raise httpx.ConnectTimeout("timeout")
        return _mock_response(404)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_worldbank("US")

    assert result.gdp_per_capita_usd is None
    assert result.inflation_rate_pct == 4.8
    assert result.ease_of_doing_business_rank is None
    assert result.source_year == 2023


@pytest.mark.asyncio
async def test_unknown_region_zero_requests(monkeypatch):
    called = False

    async def mock_get(self, url, *args, **kwargs):
        nonlocal called
        called = True
        return _mock_response(200)

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_worldbank("UnknownLand")

    assert called is False
    assert result == MarketData()
    assert result.gdp_per_capita_usd is None
    assert result.source_year is None


@pytest.mark.asyncio
async def test_null_values_in_response(monkeypatch):
    async def mock_get(self, url, *args, **kwargs):
        return _mock_response(200, [{"page": 1}, [{"date": "2021", "value": None}]])

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_worldbank("GB")

    assert result.gdp_per_capita_usd is None
    assert result.inflation_rate_pct is None
    assert result.ease_of_doing_business_rank is None
    assert result.source_year is None
