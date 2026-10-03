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
    """Fetch up to 5 recent news articles for region + industry."""
    raise NotImplementedError("Phase 5")
