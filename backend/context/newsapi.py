import hashlib
import time
from typing import Any
import httpx
try:
    from backend.config import settings
    from backend.models.context import NewsItem
except ImportError:
    from config import settings
    from models.context import NewsItem

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

_CACHE: dict[str, tuple[float, list[NewsItem]]] = {}
_CACHE_TTL_SECONDS: float = 3600.0


def _cache_key(region: str, industry: str) -> str:
    r = region.strip().lower() if isinstance(region, str) else ""
    ind = industry.strip().lower() if isinstance(industry, str) else ""
    return hashlib.md5(f"{r}:{ind}".encode("utf-8")).hexdigest()


def _get_from_cache(region_or_key: str, industry: str | None = None) -> list[NewsItem] | None:
    if industry is not None:
        key = _cache_key(region_or_key, industry)
    elif isinstance(region_or_key, str) and len(region_or_key) == 32 and region_or_key.isalnum():
        key = region_or_key
    else:
        key = str(region_or_key)
    cached_entry = _CACHE.get(key)
    if cached_entry is None:
        return None
    timestamp, items = cached_entry
    if (time.time() - timestamp) < _CACHE_TTL_SECONDS:
        return items
    _CACHE.pop(key, None)
    return None


_get_cached = _get_from_cache


def _set_cache(region_or_key: str, industry_or_items: Any, items: list[NewsItem] | None = None) -> None:
    if items is not None:
        key = _cache_key(region_or_key, industry_or_items)
        items_to_cache = items
    elif isinstance(industry_or_items, list):
        key = region_or_key
        items_to_cache = industry_or_items
    else:
        key = str(region_or_key)
        items_to_cache = []
    _CACHE[key] = (time.time(), items_to_cache)




async def fetch_news(region: str, industry: str) -> list[NewsItem]:
    if not isinstance(region, str) or not isinstance(industry, str):
        return []

    clean_region = region.strip().lower()
    clean_industry = industry.strip().lower()
    key = _cache_key(clean_region, clean_industry)

    cached = _get_from_cache(key)
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
            articles = []
            if response.is_success:
                data = response.json()
                articles = data.get("articles", []) if isinstance(data.get("articles"), list) else []

            # If top-headlines returned 0, try /v2/everything with country + industry
            if not articles:
                country_name = clean_region.upper()
                query_str = f"{country_name} {clean_industry}" if clean_industry else country_name
                ev_url = "https://newsapi.org/v2/everything"
                ev_params = {
                    "q": query_str,
                    "sortBy": "relevancy",
                    "pageSize": 5,
                }
                ev_resp = await client.get(ev_url, headers=headers, params=ev_params)
                if ev_resp.is_success:
                    ev_data = ev_resp.json()
                    articles = ev_data.get("articles", []) if isinstance(ev_data.get("articles"), list) else []

            news_items: list[NewsItem] = []
            for art in articles:
                if not isinstance(art, dict):
                    continue
                title = art.get("title")
                if not title:
                    continue
                source_obj = art.get("source")
                source_name = (
                    source_obj.get("name") if isinstance(source_obj, dict) and source_obj.get("name") else "NewsAPI"
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
                _set_cache(key, news_items)
            return news_items
    except Exception:
        return []
