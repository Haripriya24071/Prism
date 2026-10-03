"""backend/models/context.py — Pydantic models for context harvester outputs."""

from typing import List, Optional
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """News item from NewsAPI."""

    headline: str
    date: str
    source: str
    url: str


class MarketData(BaseModel):
    """Economic market data from World Bank Open Data."""

    gdp_usd: Optional[float] = None
    ease_of_business_rank: Optional[int] = None
    inflation_pct: Optional[float] = None
    fdi_inflow_usd: Optional[float] = None


class CompetitorItem(BaseModel):
    """Competitor information from Crunchbase Basic or fallback."""

    name: str
    funding: Optional[str] = None
    stage: Optional[str] = None
    founded: Optional[str] = None


class ContextPackage(BaseModel):
    """Aggregated real-time context from all 5 harvester sources."""

    news: List[NewsItem] = Field(default_factory=list)
    market: MarketData = Field(default_factory=MarketData)
    competitors: List[CompetitorItem] = Field(default_factory=list)
    regulatory: List[str] = Field(default_factory=list)
    cultural: Optional[str] = None
