"""backend/output/investor_score.py — Pure math weighted sum calculation of investor score."""

from backend.models.agents import ScoreMatrix
from backend.models.output import InvestorScore


def calculate_investor_score(score_matrix: ScoreMatrix) -> InvestorScore:
    raise NotImplementedError("Phase 9")
