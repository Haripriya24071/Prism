"""backend/tests/test_newsapi.py — Unit tests for NewsAPI client."""

from typing import Any
import httpx
import pytest
from backend.config import settings
from backend.context.newsapi import _CACHE, fetch_news
from backend.models.context import NewsItem


def _mock_response(status_code: int, json_data: Any = None) -> httpx.Response:
    request = httpx.Request("GET", "https://newsapi.org/v2/top-headlines")
    return httpx.Response(status_code=status_code, json=json_data, request=request)


@pytest.fixture(autouse=True)
def clear_cache():
    _CACHE.clear()
    yield
    _CACHE.clear()


@pytest.mark.asyncio
async def test_fetch_news_success(monkeypatch):
    monkeypatch.setattr(settings, "NEWSAPI_KEY", "test-key-123")
    captured_headers = {}

    async def mock_get(self, url, headers=None, params=None, *args, **kwargs):
        nonlocal captured_headers
        captured_headers = headers or {}
        return _mock_response(
            200,
            {
                "status": "ok",
                "totalResults": 2,
                "articles": [
                    {
                        "source": {"id": "reuters", "name": "Reuters"},
                        "author": "John Doe",
                        "title": "Tech Boom in India",
                        "description": "Startups booming in 2026",
                        "url": "https://reuters.com/tech-boom",
                        "publishedAt": "2026-03-15T08:00:00Z",
                        "content": "Article content",
                    },
                    {
                        "source": {"id": None, "name": "TechCrunch"},
                        "author": None,
                        "title": "AI in Agritech",
                        "description": "Agritech investments grow",
                        "url": "https://techcrunch.com/agritech",
                        "publishedAt": "2026-03-14T10:00:00Z",
                        "content": None,
                    },
                ],
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    items = await fetch_news("India", "Fintech")

    assert len(items) == 2
    assert isinstance(items[0], NewsItem)
    assert items[0].title == "Tech Boom in India"
    assert items[0].source == "Reuters"
    assert items[0].url == "https://reuters.com/tech-boom"
    assert items[1].source == "TechCrunch"
    assert captured_headers.get("X-Api-Key") == "test-key-123"


@pytest.mark.asyncio
async def test_cache_hits_without_network(monkeypatch):
    monkeypatch.setattr(settings, "NEWSAPI_KEY", "test-key-123")
    call_count = 0

    async def mock_get(self, url, *args, **kwargs):
        nonlocal call_count
        call_count += 1
        return _mock_response(
            200,
            {
                "status": "ok",
                "articles": [
                    {"title": "Cached News", "source": {"name": "BBC"}, "url": "https://bbc.com"}
                ],
            },
        )

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    first_call = await fetch_news("US", "AI")
    assert call_count == 1
    assert len(first_call) == 1

    second_call = await fetch_news("US", "AI")
    assert call_count == 1
    assert len(second_call) == 1
    assert second_call[0].title == "Cached News"


@pytest.mark.asyncio
async def test_missing_api_key_returns_empty(monkeypatch):
    monkeypatch.setattr(settings, "NEWSAPI_KEY", "")

    items = await fetch_news("IN", "Healthcare")
    assert items == []


@pytest.mark.asyncio
async def test_http_error_returns_empty(monkeypatch):
    monkeypatch.setattr(settings, "NEWSAPI_KEY", "test-key-123")

    async def mock_get(self, url, *args, **kwargs):
        return _mock_response(429, {"status": "error", "message": "rate limited"})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    items = await fetch_news("IN", "Healthcare")
    assert items == []


@pytest.mark.asyncio
async def test_timeout_returns_empty(monkeypatch):
    monkeypatch.setattr(settings, "NEWSAPI_KEY", "test-key-123")

    async def mock_get(self, url, *args, **kwargs):
        raise httpx.ReadTimeout("Request timed out")

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

    items = await fetch_news("IN", "Fintech")
    assert items == []
