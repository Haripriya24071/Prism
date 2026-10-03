"""backend/evaluation/evaluator.py — Scores all agent BRDs across rubric criteria."""

from backend.models.agents import AgentOutput, ScoreMatrix
from backend.models.context import ContextPackage


async def evaluate_all_agents(agent_outputs: list[AgentOutput], context: ContextPackage) -> ScoreMatrix:
    raise NotImplementedError("Phase 7")
