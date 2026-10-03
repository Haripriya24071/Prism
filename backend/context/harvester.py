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
    """Aggregates all 5 context sources in parallel."""
    raise NotImplementedError("Phase 5")
