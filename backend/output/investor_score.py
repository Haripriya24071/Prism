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


def calculate_investor_score(score_matrix: ScoreMatrix) -> InvestorScore:
    """Computes investor readiness score as a weighted average across all non-failed agents.

    Flags any criterion averaging below 60 as a gap. Pure math — no I/O.
    """
    if not score_matrix.scores:
        return InvestorScore(
            session_id=score_matrix.session_id,
            score=0,
            confidence_band="needs_work",
            gap_flags=[],
        )

    # Compute per-criterion average across all agents
    criterion_totals: dict[str, list[float]] = {c: [] for c in SCORING_CRITERIA}
    for section_score in score_matrix.scores.values():
        for criterion in SCORING_CRITERIA:
            val = getattr(section_score, criterion, None)
            if val is not None:
                criterion_totals[criterion].append(float(val))

    criterion_averages: dict[str, float] = {}
    for criterion, vals in criterion_totals.items():
        criterion_averages[criterion] = sum(vals) / len(vals) if vals else 0.0

    # Weighted composite
    weighted_sum = sum(
        criterion_averages[c] * meta["weight"]
        for c, meta in SCORING_CRITERIA.items()
    )
    final_score = max(0, min(100, int(round(weighted_sum))))

    # Gap flags — any criterion average below threshold
    gap_flags: list[GapFlag] = []
    for criterion, avg in criterion_averages.items():
        if avg < _GAP_THRESHOLD:
            gap_flags.append(
                GapFlag(
                    criterion=criterion.replace("_", " ").title(),
                    score=int(round(avg)),
                    action_item=_ACTION_ITEMS.get(criterion, "Review and strengthen this area"),
                )
            )

    confidence_band = _get_confidence_band(final_score)

    logger.info(
        "investor_score_calculated",
        session_id=score_matrix.session_id,
        score=final_score,
        confidence_band=confidence_band,
        gap_count=len(gap_flags),
    )

    return InvestorScore(
        session_id=score_matrix.session_id,
        score=final_score,
        confidence_band=confidence_band,
        gap_flags=gap_flags,
    )
