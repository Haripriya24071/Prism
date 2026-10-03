"""backend/context/crunchbase.py — Crunchbase Basic integration client."""

from typing import Any, TYPE_CHECKING
import httpx
import structlog

if TYPE_CHECKING:
    from backend.config import settings
else:
    try:
        from backend.config import settings
    except ImportError:
        from config import settings

logger = structlog.get_logger()

_TIMEOUT = 5.0
_CRUNCHBASE_URL = "https://api.crunchbase.com/api/v4/searches/organizations"

# Static fallback — used when key is absent or API call fails
# Labelled clearly so demo commentary can reference it honestly
_STATIC_FALLBACK: dict[str, dict[str, Any]] = {
    "fintech": {
        "recent_rounds": [
            {"company": "Example Fintech Co", "amount_usd": 2_000_000, "round": "Seed", "year": 2024},
            {"company": "PayFlow India", "amount_usd": 5_000_000, "round": "Series A", "year": 2024},
        ],
        "total_funding_usd": 7_000_000,
        "data_source": "static_fallback",
        "note": "Live Crunchbase data unavailable — using representative static dataset for demo",
    },
    "edtech": {
        "recent_rounds": [
            {"company": "LearnPath", "amount_usd": 1_500_000, "round": "Seed", "year": 2024},
        ],
        "total_funding_usd": 1_500_000,
        "data_source": "static_fallback",
        "note": "Live Crunchbase data unavailable — using representative static dataset for demo",
    },
    "healthtech": {
        "recent_rounds": [
            {"company": "MedTrack", "amount_usd": 3_000_000, "round": "Seed", "year": 2024},
        ],
        "total_funding_usd": 3_000_000,
        "data_source": "static_fallback",
        "note": "Live Crunchbase data unavailable — using representative static dataset for demo",
    },
}

_DEFAULT_FALLBACK: dict[str, Any] = {
    "recent_rounds": [],
    "total_funding_usd": None,
    "data_source": "static_fallback",
    "note": "Live Crunchbase data unavailable — using representative static dataset for demo",
}


def _get_fallback(industry: str) -> dict[str, Any]:
    """Retrieve matched or default static fallback dictionary for industry."""
    industry_lower = industry.lower()
    for key in _STATIC_FALLBACK:
        if key in industry_lower:
            return _STATIC_FALLBACK[key]
    return _DEFAULT_FALLBACK


async def fetch_crunchbase(industry: str) -> dict[str, Any]:
    """Fetch recent funding rounds for an industry."""
    raise NotImplementedError("Phase 5")
