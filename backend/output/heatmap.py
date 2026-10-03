"""backend/output/heatmap.py — Pure math calculation of section risk heatmap."""

from backend.models.agents import ScoreMatrix
from backend.models.output import HeatmapData


def calculate_heatmap(score_matrix: ScoreMatrix) -> HeatmapData:
    raise NotImplementedError("Phase 9")
