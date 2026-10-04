"""backend/context/worldbank.py — World Bank Open Data integration client."""

import asyncio
from typing import Any
import httpx
from backend.config import settings
from backend.models.context import MarketData

_COUNTRY_MAP: dict[str, str] = {
    "in": "IN",
    "india": "IN",
    "us": "US",
    "united states": "US",
    "usa": "US",
    "gb": "GB",
    "uk": "GB",
    "united kingdom": "GB",
    "sg": "SG",
    "singapore": "SG",
    "ae": "AE",
    "uae": "AE",
    "united arab emirates": "AE",
    "de": "DE",
    "germany": "DE",
}


async def _fetch_indicator(
    client: httpx.AsyncClient, code: str, indicator: str
) -> tuple[Any | None, int | None]:
    url = f"https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&mrnev=1"
    for attempt in range(2):
        try:
            response = await client.get(url)
            if response.status_code in (502, 503) and attempt == 0:
                await asyncio.sleep(0.5)
                continue
            if not response.is_success:
                return None, None
            data = response.json()
            if isinstance(data, list) and len(data) > 1 and data[1]:
                entry = data[1][0]
                val = entry.get("value")
                year_str = entry.get("date")
                parsed_year = (
                    int(year_str)
                    if (year_str and str(year_str).isdigit() and val is not None)
                    else None
                )
                return val, parsed_year
            return None, None
        except Exception:
            if attempt == 0:
                await asyncio.sleep(0.5)
                continue
            return None, None
    return None, None


async def fetch_worldbank(region: str) -> MarketData:
    if not isinstance(region, str):
        return MarketData()
    clean_region = region.strip().lower()
    country_code = _COUNTRY_MAP.get(clean_region)
    if not country_code:
        return MarketData()

    timeout = httpx.Timeout(settings.HARVESTER_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        gdp_task = _fetch_indicator(client, country_code, "NY.GDP.PCAP.CD")
        inflation_task = _fetch_indicator(client, country_code, "FP.CPI.TOTL.ZG")
        ease_task = _fetch_indicator(client, country_code, "IC.BUS.EASE.XQ")

        (gdp_val, gdp_year), (inf_val, inf_year), (ease_val, ease_year) = await asyncio.gather(
            gdp_task, inflation_task, ease_task, return_exceptions=False
        )

    gdp_float: float | None = float(gdp_val) if gdp_val is not None else None
    inf_float: float | None = float(inf_val) if inf_val is not None else None
    ease_int: int | None = int(ease_val) if ease_val is not None else None

    years: list[int] = [y for y in (gdp_year, inf_year, ease_year) if y is not None]
    source_year: int | None = max(years) if years else None

    return MarketData(
        gdp_per_capita_usd=gdp_float,
        ease_of_doing_business_rank=ease_int,
        inflation_rate_pct=inf_float,
        source_year=source_year,
    )
