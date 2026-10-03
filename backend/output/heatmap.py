"""backend/output/heatmap.py — Pure math calculation of section risk heatmap."""

import statistics
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.agents import ScoreMatrix
    from backend.models.output import HeatmapData, HeatmapBar
else:
    try:
        from backend.models.agents import ScoreMatrix
        from backend.models.output import HeatmapData, HeatmapBar
    except ImportError:
        from models.agents import ScoreMatrix
        from models.output import HeatmapData, HeatmapBar

logger = structlog.get_logger()

_CRITERIA_ORDER = [
    "feasibility",
    "market_timing",
    "regulatory_safety",
    "user_adoption",
    "competitive_moat",
]


def _normalise_std_to_risk(std_dev: float, max_possible_std: float = 50.0) -> int:
    """Convert std dev (0 to ~50) to a 0-100 risk score.

    std_dev of 0 = full consensus = risk 0. std_dev of 50 = maximum possible disagreement = risk 100.
    """
    normalised = (std_dev / max_possible_std) * 100
    return max(0, min(100, int(round(normalised))))
