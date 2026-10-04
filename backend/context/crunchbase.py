"""backend/context/crunchbase.py — Crunchbase integration client with fallback data."""

from typing import Any
import httpx
from backend.config import settings

_STATIC_COMPETITORS: dict[str, list[dict[str, str]]] = {
    "fintech": [
        {"name": "Stripe", "funding": "$8.7B", "stage": "Late Stage", "founded": "2010"},
        {"name": "Razorpay", "funding": "$816M", "stage": "Series F", "founded": "2014"},
        {"name": "Plaid", "funding": "$734M", "stage": "Series D", "founded": "2013"},
    ],
    "healthtech": [
        {"name": "Oscar Health", "funding": "$1.6B", "stage": "Public", "founded": "2012"},
        {"name": "Practo", "funding": "$228M", "stage": "Series D", "founded": "2008"},
        {"name": "HealthifyMe", "funding": "$130M", "stage": "Series C", "founded": "2012"},
    ],
    "edtech": [
        {"name": "Coursera", "funding": "$443M", "stage": "Public", "founded": "2012"},
        {"name": "Duolingo", "funding": "$183M", "stage": "Public", "founded": "2011"},
        {"name": "Unacademy", "funding": "$880M", "stage": "Series H", "founded": "2015"},
    ],
    "agritech": [
        {"name": "Indigo Ag", "funding": "$1.2B", "stage": "Series F", "founded": "2013"},
        {"name": "DeHaat", "funding": "$221M", "stage": "Series E", "founded": "2012"},
        {"name": "Ninjacart", "funding": "$377M", "stage": "Series D", "founded": "2015"},
    ],
}

_DEFAULT_COMPETITORS: list[dict[str, str]] = [
    {"name": "Market Leader Alpha", "funding": "$50M+", "stage": "Series B", "founded": "2018"},
    {"name": "Emerging Tech Beta", "funding": "$15M", "stage": "Series A", "founded": "2021"},
]


def _get_fallback_data(industry: str) -> dict[str, Any]:
    clean_industry = industry.strip().lower() if isinstance(industry, str) else "general"
    matched_competitors = _STATIC_COMPETITORS.get(clean_industry)
    is_known = matched_competitors is not None
    if not matched_competitors:
        for key, comps in _STATIC_COMPETITORS.items():
            if key in clean_industry or clean_industry in key:
                matched_competitors = comps
                is_known = True
                break
    if not matched_competitors:
        matched_competitors = _DEFAULT_COMPETITORS

    recent_rounds = (
        [{"company": c["name"], "round": c["stage"], "amount": c["funding"], "year": c["founded"]} for c in matched_competitors]
        if is_known
        else []
    )

    return {
        "source": "crunchbase_static_fallback",
        "data_source": "static_fallback",
        "industry": industry,
        "competitors": matched_competitors,
        "recent_rounds": recent_rounds,
        "market_stage_trend": "Growing",
        "cached": True,
    }


_get_fallback = _get_fallback_data



async def fetch_crunchbase(industry: str) -> dict[str, Any]:
    if not isinstance(industry, str) or not industry.strip():
        return _get_fallback_data("general")

    clean_industry = industry.strip()
    if not settings.CRUNCHBASE_KEY or not settings.CRUNCHBASE_KEY.strip():
        return _get_fallback_data(clean_industry)

    url = "https://api.crunchbase.com/api/v4/autocompletes"
    headers = {"X-cb-user-key": settings.CRUNCHBASE_KEY}
    params = {"query": clean_industry, "limit": 5}
    timeout = httpx.Timeout(settings.HARVESTER_TIMEOUT_SECONDS)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code in (401, 403) or not response.is_success:
                return _get_fallback_data(clean_industry)

            data = response.json()
            entities = data.get("entities", [])
            competitors: list[dict[str, str]] = []
            for item in entities:
                identifier = item.get("identifier", {})
                name = identifier.get("value")
                if name:
                    competitors.append(
                        {
                            "name": str(name),
                            "funding": "Disclosed in API",
                            "stage": "Active",
                            "founded": "N/A",
                        }
                    )

            if not competitors:
                return _get_fallback_data(clean_industry)

            return {
                "source": "crunchbase_api",
                "industry": clean_industry,
                "competitors": competitors,
                "cached": False,
            }
    except Exception:
        return _get_fallback_data(clean_industry)
