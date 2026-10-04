"""backend/tests/test_crunchbase.py — Unit tests for Crunchbase client."""

from typing import Any
import httpx
import pytest
from backend.config import settings
from backend.context.crunchbase import fetch_crunchbase


def _mock_response(status_code: int, json_data: Any = None) -> httpx.Response:
    request = httpx.Request("GET", "https://api.crunchbase.com/api/v4/autocompletes")
    return httpx.Response(status_code=status_code, json=json_data, request=request)


@pytest.mark.asyncio
async def test_missing_key_uses_static_fallback(monkeypatch):
    monkeypatch.setattr(settings, "CRUNCHBASE_KEY", "")

    result = await fetch_crunchbase("Fintech")

    assert result["source"] == "crunchbase_static_fallback"
    assert result["cached"] is True
    assert len(result["competitors"]) >= 2
    assert any(c["name"] == "Razorpay" for c in result["competitors"])


@pytest.mark.asyncio
async def test_401_or_403_falls_back_to_static(monkeypatch):
    monkeypatch.setattr(settings, "CRUNCHBASE_KEY", "invalid_key")

    async def mock_get(self, url, *args, **kwargs):
        return _mock_response(401, {"message": "Unauthorized"})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_crunchbase("Healthtech")

    assert result["source"] == "crunchbase_static_fallback"
    assert result["cached"] is True
    assert any(c["name"] == "Practo" for c in result["competitors"])


@pytest.mark.asyncio
async def test_api_success(monkeypatch):
    monkeypatch.setattr(settings, "CRUNCHBASE_KEY", "valid_key")
    captured_headers = {}

    async def mock_get(self, url, headers=None, *args, **kwargs):
        nonlocal captured_headers
        captured_headers = headers or {}
        return _mock_response(
            200,
            {
                "entities": [
                    {"identifier": {"value": "Acme Fintech", "uuid": "123"}},
                    {"identifier": {"value": "Beta Payments", "uuid": "456"}},
                ]
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_crunchbase("Fintech")

    assert result["source"] == "crunchbase_api"
    assert result["cached"] is False
    assert len(result["competitors"]) == 2
    assert result["competitors"][0]["name"] == "Acme Fintech"
    assert captured_headers.get("X-cb-user-key") == "valid_key"


@pytest.mark.asyncio
async def test_network_timeout_uses_fallback(monkeypatch):
    monkeypatch.setattr(settings, "CRUNCHBASE_KEY", "valid_key")

    async def mock_get(self, url, *args, **kwargs):
        raise httpx.ConnectTimeout("Connection timed out")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    result = await fetch_crunchbase("Edtech")

    assert result["source"] == "crunchbase_static_fallback"
    assert result["cached"] is True
    assert any(c["name"] == "Coursera" for c in result["competitors"])
