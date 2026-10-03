"""backend/context/harvester.py — Aggregates all 5 context sources in parallel."""

import asyncio
import time
from typing import Any, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.intake import IntakePackage
    from backend.models.context import ContextPackage, NewsItem, MarketData
    from backend.context.newsapi import fetch_news
    from backend.context.worldbank import fetch_worldbank
    from backend.context.crunchbase import fetch_crunchbase
    from backend.context.govtdata import fetch_govtdata
    from backend.context.grounding import fetch_gemini_grounding
    from backend.gcp.bigquery import log_context_harvest
else:
    try:
        from backend.models.intake import IntakePackage
        from backend.models.context import ContextPackage, NewsItem, MarketData
        from backend.context.newsapi import fetch_news
        from backend.context.worldbank import fetch_worldbank
        from backend.context.crunchbase import fetch_crunchbase
        from backend.context.govtdata import fetch_govtdata
        from backend.context.grounding import fetch_gemini_grounding
        from backend.gcp.bigquery import log_context_harvest
    except ImportError:
        from models.intake import IntakePackage
        from models.context import ContextPackage, NewsItem, MarketData
        from context.newsapi import fetch_news
        from context.worldbank import fetch_worldbank
        from context.crunchbase import fetch_crunchbase
        from context.govtdata import fetch_govtdata
        from context.grounding import fetch_gemini_grounding
        from gcp.bigquery import log_context_harvest

logger = structlog.get_logger()


async def _safe_fetch(coro: Any, source_name: str) -> tuple[str, Any]:
    """Wraps any fetch coroutine — returns (source_name, result) or (source_name, None) on failure."""
    start = time.time()
    try:
        result = await coro
        elapsed_ms = int((time.time() - start) * 1000)
        logger.info("context_source_ok", source=source_name, elapsed_ms=elapsed_ms)
        return source_name, result
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        logger.warning(
            "context_source_failed",
            source=source_name,
            elapsed_ms=elapsed_ms,
            error_type=type(e).__name__,
        )
        return source_name, None


async def harvest_context(intake: IntakePackage) -> ContextPackage:
    """Runs all 5 context sources in parallel via asyncio.gather.

    Partial failure is allowed — failed sources are recorded in ContextPackage.failed_sources. Never
    raises. Target: < 8 seconds total.
    """
    region = intake.extraction.region or ""
    industry = intake.extraction.industry or ""

    harvest_start = time.time()
    logger.info("harvest_start", session_id=intake.session_id, region=region, industry=industry)

    results = await asyncio.gather(
        _safe_fetch(fetch_news(region, industry), "newsapi"),
        _safe_fetch(fetch_worldbank(region), "worldbank"),
        _safe_fetch(fetch_crunchbase(industry), "crunchbase"),
        _safe_fetch(fetch_govtdata(region, industry), "govtdata"),
        _safe_fetch(fetch_gemini_grounding(region, industry), "grounding"),
        return_exceptions=True,
    )

    # Unpack results — each is (source_name, value) or an Exception
    source_map: dict[str, Any] = {}
    failed: list[str] = []
    for result in results:
        if isinstance(result, tuple):
            source_name, value = result
            if value is None:
                failed.append(source_name)
            else:
                source_map[source_name] = value
        elif isinstance(result, BaseException):
            logger.error("harvest_gather_exception", error_type=type(result).__name__)

    raw_news = source_map.get("newsapi")
    news_items: list[NewsItem] = raw_news if isinstance(raw_news, list) else []

    raw_market = source_map.get("worldbank")
    market_data: MarketData | None = raw_market if hasattr(raw_market, "gdp_per_capita_usd") or raw_market is None else None

    crunchbase_raw = source_map.get("crunchbase") or {}
    govtdata_raw = source_map.get("govtdata") or {}
    cultural_ctx = source_map.get("grounding") or None

    elapsed_ms = int((time.time() - harvest_start) * 1000)
    logger.info(
        "harvest_complete",
        session_id=intake.session_id,
        elapsed_ms=elapsed_ms,
        sources_ok=len(source_map),
        sources_failed=len(failed),
    )

    # Fire BigQuery logging as background task — never blocks
    from gcp.bigquery import log_context_harvest

    asyncio.create_task(
        log_context_harvest(
            session_id=intake.session_id,
            sources=list(source_map.keys()),
            duration_ms=elapsed_ms,
        )
    )

    return ContextPackage(
        session_id=intake.session_id,
        region=region or None,
        industry=industry or None,
        news_items=news_items,
        market_data=market_data,
        crunchbase_data=crunchbase_raw,
        regulatory_flags=govtdata_raw.get("regulatory_flags", []),
        cultural_context=cultural_ctx,
        source_urls=[item.url for item in news_items if item.url],
        failed_sources=failed,
    )
