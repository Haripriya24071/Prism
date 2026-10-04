"""backend/context/gdelt.py — GDELT Project open political events & regulatory news harvester."""

import logging
import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
_TIMEOUT = 6.0
_COUNTRY_NAMES: dict[str, str] = {
    "IN": "India",
    "US": "United States",
    "GB": "United Kingdom",
    "SG": "Singapore",
    "NG": "Nigeria",
    "DE": "Germany",
    "BR": "Brazil",
    "AU": "Australia",
    "CA": "Canada",
    "AE": "UAE",
    "ZA": "South Africa",
    "JP": "Japan",
}


async def fetch_political_context(region: str, industry: str) -> dict:
    """Fetch political events for region via GDELT.

    Completely free — no API key needed. Never raises.
    """
    if not region or not isinstance(region, str):
        return {}
    country = _COUNTRY_NAMES.get(region.strip().upper(), region.strip())
    industry_clean = industry.strip() if isinstance(industry, str) else "business"
    params = {
        "query": f"{country} government policy regulation {industry_clean}",
        "mode": "artlist",
        "maxrecords": "5",
        "format": "json",
        "timespan": "2months",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        articles = data.get("articles", [])
        events = [
            {
                "title": a.get("title", ""),
                "url": a.get("url", ""),
                "date": a.get("seendate", ""),
                "source": a.get("domain", ""),
            }
            for a in articles[:5]
            if a.get("title")
        ]
        logger.info("gdelt_fetched: region=%s, count=%d", region, len(events))
        return {
            "political_events": events,
            "country": country,
            "data_source": "gdelt_project",
        }
    except Exception as e:
        logger.warning("gdelt_failed: region=%s, error_type=%s", region, type(e).__name__)
        return {}
