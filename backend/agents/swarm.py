"""backend/agents/swarm.py — Orchestrates parallel execution of all 6 swarm agents."""

from collections.abc import Callable, Awaitable
from backend.models.intake import IntakePackage
from backend.models.context import ContextPackage
from backend.models.agents import AgentOutput


async def run_swarm(
    intake: IntakePackage,
    context: ContextPackage,
    session_id: str,
    progress_callback: Callable[[str, str], Awaitable[None]] | None = None,
) -> list[AgentOutput]:
    raise NotImplementedError("Phase 6")
