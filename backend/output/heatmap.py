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


def calculate_heatmap(score_matrix: ScoreMatrix) -> HeatmapData:
    """For each scoring criterion, compute the std dev of scores across all agents.

    Normalise to 0-100 risk scale. Higher = more agent disagreement = higher risk. Pure math — no I/O, no
    Vertex AI.
    """
    bars: list[HeatmapBar] = []

    for criterion in _CRITERIA_ORDER:
        scores_for_criterion = []
        for agent_key, section_score in score_matrix.scores.items():
            raw = getattr(section_score, criterion, None)
            if raw is not None:
                scores_for_criterion.append(float(raw))

        if len(scores_for_criterion) < 2:
            std_dev = 0.0
        else:
            std_dev = statistics.stdev(scores_for_criterion)

        risk_score = _normalise_std_to_risk(std_dev)

        bars.append(
            HeatmapBar(
                section_title=criterion.replace("_", " ").title(),
                risk_score=risk_score,
                std_dev=round(std_dev, 2),
            )
        )

    logger.info(
        "heatmap_calculated",
        session_id=score_matrix.session_id,
        criteria_count=len(bars),
        max_risk=max((b.risk_score for b in bars), default=0),
    )

    return HeatmapData(session_id=score_matrix.session_id, bars=bars)
