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
    """Fetch GDP per capita, ease of doing business, inflation for a region.

    All three indicators fetched in parallel. Returns MarketData with None for failed fields. Never
    raises — failed fields silently become None.
    """
    if not region:
        return MarketData()

    logger.info("worldbank_fetch_start", region=region)

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            results = await asyncio.gather(
                *[
                    _fetch_indicator(client, region, field, indicator)
                    for field, indicator in _INDICATORS.items()
                ],
                return_exceptions=True,
            )
    except Exception as e:
        logger.warning("worldbank_gather_failed", error_type=type(e).__name__)
        return MarketData()

    values: dict[str, float | None] = {}
    for result in results:
        if isinstance(result, tuple):
            field, value = result
            values[field] = value

    ease_rank = values.get("ease_of_doing_business_rank")
    market_data = MarketData(
        gdp_per_capita_usd=values.get("gdp_per_capita_usd"),
        ease_of_doing_business_rank=int(ease_rank) if ease_rank is not None else None,
        inflation_rate_pct=values.get("inflation_rate_pct"),
        source_year=2023,
    )

    logger.info(
        "worldbank_fetch_complete",
        region=region,
        gdp_available=market_data.gdp_per_capita_usd is not None,
        biz_rank_available=market_data.ease_of_doing_business_rank is not None,
    )
    return market_data
