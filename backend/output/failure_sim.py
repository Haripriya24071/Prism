"""backend/output/failure_sim.py — Extracts failure modes from Adversarial agent output."""

from backend.models.agents import AgentOutput
from backend.models.brd import FailureMode


async def extract_failure_modes(adversarial_output: AgentOutput) -> list[FailureMode]:
    raise NotImplementedError("Phase 9")
