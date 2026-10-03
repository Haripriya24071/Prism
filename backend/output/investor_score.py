"""backend/output/investor_score.py — Pure math weighted sum calculation of investor score."""

from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.agents import ScoreMatrix
    from backend.models.output import InvestorScore, GapFlag
    from backend.evaluation.rubric import SCORING_CRITERIA
else:
    try:
        from backend.models.agents import ScoreMatrix
        from backend.models.output import InvestorScore, GapFlag
        from backend.evaluation.rubric import SCORING_CRITERIA
    except ImportError:
        from models.agents import ScoreMatrix
        from models.output import InvestorScore, GapFlag
        from evaluation.rubric import SCORING_CRITERIA

logger = structlog.get_logger()

_GAP_THRESHOLD = 60

_ACTION_ITEMS: dict[str, str] = {
    "feasibility": "Validate core assumptions with at least 3 paying customers before building",
    "market_timing": "Research why now — identify the market trigger that makes this the right moment",
    "regulatory_safety": "Engage a local legal advisor to map compliance obligations before launch",
    "user_adoption": "Run 5 user interviews to confirm the problem exists and the solution resonates",
    "competitive_moat": "Define one defensible differentiator — network effect, data moat, or switching cost",
}

_CONFIDENCE_BANDS = [
    (70, "fundable"),
    (50, "promising"),
    (0, "needs_work"),
]


def _get_confidence_band(score: int) -> str:
    for threshold, label in _CONFIDENCE_BANDS:
        if score >= threshold:
            return label
    return "needs_work"
