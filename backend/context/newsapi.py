"""backend/context/newsapi.py — NewsAPI integration client."""

from backend.models.context import NewsItem


async def fetch_news(region: str, industry: str) -> list[NewsItem]:
    raise NotImplementedError("Phase 5")
