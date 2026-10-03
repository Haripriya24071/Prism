"""backend/context/worldbank.py — World Bank Open Data integration client."""

from backend.models.context import MarketData


async def fetch_worldbank(region: str) -> MarketData:
    raise NotImplementedError("Phase 5")
