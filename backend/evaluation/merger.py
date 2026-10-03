"""backend/evaluation/merger.py — Merges top agent sections into unified BRD."""

from backend.models.agents import AgentOutput, ScoreMatrix
from backend.models.context import ContextPackage
from backend.models.brd import MergedBRD


async def merge_brds(agent_outputs: list[AgentOutput], score_matrix: ScoreMatrix, context: ContextPackage) -> MergedBRD:
    raise NotImplementedError("Phase 8")
