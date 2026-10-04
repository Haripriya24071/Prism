"""backend/context/harvester.py — Aggregates all 7 context sources in parallel."""

import asyncio
from datetime import datetime, timezone
from typing import Any

try:
    from backend.config import settings
    from backend.context.alphavantage import fetch_market_sentiment
    from backend.context.crunchbase import fetch_crunchbase
    from backend.context.forex import fetch_forex_data
    from backend.context.gdelt import fetch_political_context
    from backend.context.geopolitics import fetch_geopolitics_and_religion
    from backend.context.govtdata import fetch_govtdata
    from backend.context.grounding import fetch_gemini_grounding
    from backend.context.newsapi import fetch_news
    from backend.context.worldbank import fetch_worldbank
    from backend.models.context import ContextPackage, MarketData, NewsItem
    from backend.models.intake import IntakePackage
except ImportError:
    from config import settings
    from context.alphavantage import fetch_market_sentiment
    from context.crunchbase import fetch_crunchbase
    from context.forex import fetch_forex_data
    from context.gdelt import fetch_political_context
    from context.geopolitics import fetch_geopolitics_and_religion
    from context.govtdata import fetch_govtdata
    from context.grounding import fetch_gemini_grounding
    from context.newsapi import fetch_news
    from context.worldbank import fetch_worldbank
    from models.context import ContextPackage, MarketData, NewsItem
    from models.intake import IntakePackage


async def harvest_context(intake: Any) -> ContextPackage:
    if intake is None or not hasattr(intake, "session_id") or not hasattr(intake, "extraction"):
        return ContextPackage(
            session_id="unknown_session",
            region=None,
            industry=None,
            failed_sources=["intake_invalid"],
        )

    session_id = str(intake.session_id)
    extraction = getattr(intake, "extraction", None)
    region = getattr(extraction, "region", None) or "IN"
    industry = getattr(extraction, "industry", None) or "General"

    tasks = [
        fetch_news(region, industry),
        fetch_worldbank(region),
        fetch_crunchbase(industry),
        fetch_govtdata(region, industry),
        fetch_gemini_grounding(region, industry),
        fetch_political_context(region, industry),
        fetch_market_sentiment(region, settings.alphavantage_key),
        fetch_geopolitics_and_religion(region),
        fetch_forex_data(region),
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
        geopolitics_res,
        forex_res,
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

    # 8. Geopolitics & Religious Dynamics
    if isinstance(geopolitics_res, Exception) or not isinstance(geopolitics_res, dict):
        failed_sources.append("geopolitics")
        geopolitical_data: dict[str, Any] = {}
        religious_context: str | None = None
    else:
        geopolitical_data = geopolitics_res
        religious_context = geopolitical_data.get("religious_demographics")

    # 9. Foreign Exchange & Currency Volatility
    if isinstance(forex_res, Exception) or not isinstance(forex_res, dict):
        failed_sources.append("forex")
        forex_data: dict[str, Any] = {}
    else:
        forex_data = forex_res

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
        religious_context=religious_context,
        geopolitical_data=geopolitical_data,
        market_sentiment=market_sentiment,
        forex_data=forex_data,
        source_urls=source_urls,
        failed_sources=failed_sources,
        harvested_at=datetime.now(timezone.utc),
    )
