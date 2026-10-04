"""backend/context/newsapi.py — NewsAPI integration client with in-memory caching."""

import time
from typing import Any
import httpx
from backend.config import settings
from backend.models.context import NewsItem

_COUNTRY_MAP: dict[str, str] = {
    "in": "in",
    "india": "in",
    "us": "us",
    "united states": "us",
    "usa": "us",
    "gb": "gb",
    "uk": "gb",
    "united kingdom": "gb",
    "ae": "ae",
    "uae": "ae",
    "united arab emirates": "ae",
    "sg": "sg",
    "singapore": "sg",
    "de": "de",
    "germany": "de",
}

_CACHE: dict[tuple[str, str], tuple[float, list[NewsItem]]] = {}
_CACHE_TTL_SECONDS: float = 3600.0


def _get_from_cache(cache_key: tuple[str, str]) -> list[NewsItem] | None:
    cached_entry = _CACHE.get(cache_key)
    if cached_entry is None:
        return None
    timestamp, items = cached_entry
    if (time.time() - timestamp) < _CACHE_TTL_SECONDS:
        return items
    _CACHE.pop(cache_key, None)
    return None


def _set_cache(cache_key: tuple[str, str], items: list[NewsItem]) -> None:
    _CACHE[cache_key] = (time.time(), items)


async def fetch_news(region: str, industry: str) -> list[NewsItem]:
    if not isinstance(region, str) or not isinstance(industry, str):
        return []

    clean_region = region.strip().lower()
    clean_industry = industry.strip().lower()
    cache_key = (clean_region, clean_industry)

    cached = _get_from_cache(cache_key)
    if cached is not None:
        return cached

    if not settings.NEWSAPI_KEY or not settings.NEWSAPI_KEY.strip():
        return []

    country_code = _COUNTRY_MAP.get(clean_region)
    params: dict[str, Any] = {
        "pageSize": 5,
    }
    if clean_industry:
        params["q"] = clean_industry
    if country_code:
        params["country"] = country_code

    headers = {"X-Api-Key": settings.NEWSAPI_KEY}
    url = "https://newsapi.org/v2/top-headlines"
    timeout = httpx.Timeout(settings.HARVESTER_TIMEOUT_SECONDS)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            if not response.is_success:
                return []
            data = response.json()
            articles = data.get("articles", [])
            if not isinstance(articles, list):
                return []

            news_items: list[NewsItem] = []
            for art in articles:
                if not isinstance(art, dict):
                    continue
                title = art.get("title")
                if not title:
                    continue
                source_obj = art.get("source")
                source_name = (
                    source_obj.get("name") if isinstance(source_obj, dict) and source_obj.get("name") else "Unknown"
                )
                item = NewsItem(
                    title=str(title),
                    source=str(source_name),
                    url=art.get("url"),
                    published_at=art.get("publishedAt"),
                    summary=art.get("description"),
                )
                news_items.append(item)

            if news_items:
                _set_cache(cache_key, news_items)
            return news_items
    except Exception:
        return []
