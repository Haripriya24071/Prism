"""backend/context/alphavantage.py — Alpha Vantage market sentiment harvester."""

import logging
import httpx

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.alphavantage.co/query"
_TIMEOUT = 5.0


async def fetch_market_sentiment(region: str, api_key: str) -> dict:
    """Fetch market sentiment via Alpha Vantage.

    Free tier: 25 requests/day. Never raises.
    """
    if not region or not api_key or not isinstance(region, str) or not isinstance(api_key, str):
        return {}
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": "economy_fiscal,financial_markets",
        "apikey": api_key.strip(),
        "limit": "5",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.get(_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
        feed = data.get("feed", [])
        scores = [
            float(item.get("overall_sentiment_score", 0))
            for item in feed
            if item.get("overall_sentiment_score") is not None
        ]
        avg = round(sum(scores) / len(scores), 3) if scores else 0.0
        mood = "bullish" if avg > 0.15 else "bearish" if avg < -0.15 else "neutral"
        logger.info("alphavantage_fetched: region=%s, mood=%s", region, mood)
        return {
            "market_sentiment_score": avg,
            "market_mood": mood,
            "data_source": "alpha_vantage",
        }
    except Exception as e:
        logger.warning("alphavantage_failed: region=%s, error_type=%s", region, type(e).__name__)
        return {}
