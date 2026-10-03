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
