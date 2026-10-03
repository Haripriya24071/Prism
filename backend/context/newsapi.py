"""backend/context/newsapi.py — NewsAPI integration client."""

import hashlib
import time
from typing import TYPE_CHECKING
import httpx
import structlog

if TYPE_CHECKING:
    from backend.models.context import NewsItem
    from backend.config import settings
else:
    try:
        from backend.models.context import NewsItem
        from backend.config import settings
    except ImportError:
        from models.context import NewsItem
        from config import settings

logger = structlog.get_logger()

_CACHE: dict[str, tuple[list[NewsItem], float]] = {}
_CACHE_TTL_SECONDS = 21_600  # 6 hours — preserve daily quota
_NEWSAPI_URL = "https://newsapi.org/v2/everything"
_TIMEOUT_SECONDS = 5.0
_MAX_RESULTS = 5


def _cache_key(region: str, industry: str) -> str:
    """Generate MD5 hash cache key from region:industry string."""
    raw = f"{region.lower()}:{industry.lower()}"
    return hashlib.md5(raw.encode()).hexdigest()


def _get_cached(region: str, industry: str) -> list[NewsItem] | None:
    """Retrieve cached news items if unexpired, else return None."""
    key = _cache_key(region, industry)
    entry = _CACHE.get(key)
    if entry is None:
        return None
    items, cached_at = entry
    if time.time() - cached_at > _CACHE_TTL_SECONDS:
        del _CACHE[key]
        return None
    logger.info("newsapi_cache_hit", region=region, industry=industry)
    return items


def _set_cache(region: str, industry: str, items: list[NewsItem]) -> None:
    """Store news items in cache with current timestamp."""
    key = _cache_key(region, industry)
    _CACHE[key] = (items, time.time())


async def fetch_news(region: str, industry: str) -> list[NewsItem]:
    """Fetch up to 5 recent news articles for region + industry.

    Returns [] on any error — never blocks the pipeline. Results cached for 6 hours to preserve
    100/day quota.
    """
    if not settings.newsapi_key:
        logger.warning("newsapi_key_not_set", region=region, industry=industry)
        return []

    cached = _get_cached(region, industry)
    if cached is not None:
        return cached

    query = f"{industry} {region} business startup"
    params: dict[str, str | int] = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": _MAX_RESULTS,
        "apiKey": settings.newsapi_key,
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT_SECONDS) as client:
            response = await client.get(_NEWSAPI_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException:
        logger.warning("newsapi_timeout", region=region, industry=industry)
        return []
    except httpx.HTTPStatusError as e:
        logger.warning("newsapi_http_error", status_code=e.response.status_code)
        return []
    except Exception as e:
        logger.warning("newsapi_unexpected_error", error_type=type(e).__name__)
        return []

    articles = data.get("articles", [])
    items = [
        NewsItem(
            title=a.get("title", ""),
            source=a.get("source", {}).get("name", ""),
            url=a.get("url"),
            published_at=a.get("publishedAt"),
            summary=a.get("description"),
        )
        for a in articles
        if a.get("title")
    ]

    _set_cache(region, industry, items)
    logger.info("newsapi_fetched", region=region, industry=industry, count=len(items))
    return items
