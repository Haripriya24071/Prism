from datetime import datetime
from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str = Field(description="Article headline")
    source: str = Field(description="Publisher name")
    url: str | None = None
    published_at: str | None = None
    summary: str | None = None


class MarketData(BaseModel):
    gdp_per_capita_usd: float | None = None
    ease_of_doing_business_rank: int | None = None
    inflation_rate_pct: float | None = None
    source_year: int | None = None


class ContextPackage(BaseModel):
    session_id: str
    region: str | None = None
    industry: str | None = None
    news_items: list[NewsItem] = Field(default_factory=list)
    market_data: MarketData | None = None
    crunchbase_data: dict = Field(default_factory=dict)
    regulatory_flags: list[str] = Field(default_factory=list)
    cultural_context: str | None = None
    political_context: dict = Field(default_factory=dict)
    religious_context: str | None = None
    geopolitical_data: dict = Field(default_factory=dict)
    market_sentiment: dict = Field(default_factory=dict)
    forex_data: dict = Field(default_factory=dict)
    source_urls: list[str] = Field(default_factory=list)
    failed_sources: list[str] = Field(default_factory=list, description="Sources that errored — partial failure allowed")
    harvested_at: datetime = Field(default_factory=datetime.utcnow)
