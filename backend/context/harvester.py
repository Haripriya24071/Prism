"""backend/context/harvester.py — Aggregates all 7 context sources in parallel."""

import asyncio
from datetime import datetime
from typing import Any

from backend.config import settings
from backend.context.alphavantage import fetch_market_sentiment
from backend.context.crunchbase import fetch_crunchbase
from backend.context.gdelt import fetch_political_context
from backend.context.govtdata import fetch_govtdata
from backend.context.grounding import fetch_gemini_grounding
from backend.context.newsapi import fetch_news
from backend.context.worldbank import fetch_worldbank
from backend.models.context import ContextPackage, MarketData, NewsItem
from backend.models.intake import IntakePackage


async def harvest_context(intake: IntakePackage) -> ContextPackage:
    if not isinstance(intake, IntakePackage):
        return ContextPackage(
            session_id="unknown_session",
            region=None,
            industry=None,
            failed_sources=["intake_invalid"],
        )

    session_id = intake.session_id
    region = intake.extraction.region or "IN"
    industry = intake.extraction.industry or "General"

    tasks = [
        fetch_news(region, industry),
        fetch_worldbank(region),
        fetch_crunchbase(industry),
        fetch_govtdata(region, industry),
        fetch_gemini_grounding(region, industry),
        fetch_political_context(region, industry),
        fetch_market_sentiment(region, settings.alphavantage_key),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    (
        news_res,
        worldbank_res,
        crunchbase_res,
        govt_res,
        grounding_res,
        gdelt_res,
        alphavantage_res,
    ) = results

    failed_sources: list[str] = []
    source_urls: list[str] = []

    # 1. NewsAPI
    if isinstance(news_res, Exception) or not isinstance(news_res, list):
        failed_sources.append("newsapi")
        news_items: list[NewsItem] = []
    else:
        news_items = news_res
        for item in news_items:
            if item.url:
                source_urls.append(item.url)

    # 2. World Bank
    if isinstance(worldbank_res, Exception) or not isinstance(worldbank_res, MarketData):
        failed_sources.append("worldbank")
        market_data: MarketData | None = None
    else:
        market_data = worldbank_res

    # 3. Crunchbase
    if isinstance(crunchbase_res, Exception) or not isinstance(crunchbase_res, dict):
        failed_sources.append("crunchbase")
        crunchbase_data: dict[str, Any] = {}
    else:
        crunchbase_data = crunchbase_res

    # 4. Govt Open Data
    if isinstance(govt_res, Exception) or not isinstance(govt_res, dict):
        failed_sources.append("govt_open_data")
        regulatory_flags: list[str] = []
    else:
        regulatory_flags = list(govt_res.get("regulatory_flags", []))

    # 5. Gemini Grounding
    if isinstance(grounding_res, Exception) or not isinstance(grounding_res, str):
        failed_sources.append("gemini_grounding")
        cultural_context: str | None = None
    else:
        cultural_context = grounding_res

    # 6. GDELT Political Context
    if isinstance(gdelt_res, Exception) or not isinstance(gdelt_res, dict):
        failed_sources.append("gdelt")
        political_context: dict[str, Any] = {}
    else:
        political_context = gdelt_res
        for event in political_context.get("political_events", []):
            if isinstance(event, dict) and event.get("url"):
                source_urls.append(event["url"])

    # 7. Alpha Vantage Market Sentiment
    if isinstance(alphavantage_res, Exception) or not isinstance(alphavantage_res, dict):
        failed_sources.append("alphavantage")
        market_sentiment: dict[str, Any] = {}
    else:
        market_sentiment = alphavantage_res

    return ContextPackage(
        session_id=session_id,
        region=region,
        industry=industry,
        news_items=news_items,
        market_data=market_data,
        crunchbase_data=crunchbase_data,
        regulatory_flags=regulatory_flags,
        cultural_context=cultural_context,
        political_context=political_context,
        market_sentiment=market_sentiment,
        source_urls=source_urls,
        failed_sources=failed_sources,
        harvested_at=datetime.utcnow(),
    )
