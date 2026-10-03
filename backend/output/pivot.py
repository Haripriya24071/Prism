"""backend/output/pivot.py — Generates pivot suggestions if score < 60."""

from backend.models.brd import MergedBRD
from backend.models.output import InvestorScore, PivotSuggestion


async def suggest_pivots(merged_brd: MergedBRD, score: InvestorScore) -> list[PivotSuggestion] | None:
    raise NotImplementedError("Phase 9")
