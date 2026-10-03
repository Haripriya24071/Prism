"""backend/context/worldbank.py — World Bank Open Data integration client."""

import asyncio
from typing import TYPE_CHECKING
import httpx
import structlog

if TYPE_CHECKING:
    from backend.models.context import MarketData
else:
    try:
        from backend.models.context import MarketData
    except ImportError:
        from models.context import MarketData

logger = structlog.get_logger()

_BASE_URL = "https://api.worldbank.org/v2/country"
_TIMEOUT = 5.0
_INDICATORS = {
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
    "ease_of_doing_business_rank": "IC.BUS.EASE.XQ",
    "inflation_rate_pct": "FP.CPI.TOTL.ZG",
}


async def _fetch_indicator(
    client: httpx.AsyncClient, region: str, field: str, indicator: str
) -> tuple[str, float | None]:
    """Fetch one World Bank indicator. Returns (field_name, value | None)."""
    url = f"{_BASE_URL}/{region}/indicator/{indicator}"
    params = {"format": "json", "mrv": "1"}
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # World Bank wraps data: [metadata_dict, [records]]
        records = data[1] if len(data) > 1 else []
        if records and records[0].get("value") is not None:
            return field, float(records[0]["value"])
        return field, None
    except Exception as e:
        logger.warning("worldbank_indicator_failed", field=field, error_type=type(e).__name__)
        return field, None


async def fetch_worldbank(region: str) -> MarketData:
    """Fetch GDP per capita, ease of doing business, inflation for a region."""
    raise NotImplementedError("Phase 5")
