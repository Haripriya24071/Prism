"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

from backend.models.intake import IntakePackage
from backend.models.context import ContextPackage
from backend.models.agents import AgentPersona


def build_agent_prompt(persona: AgentPersona, intake: IntakePackage, context: ContextPackage) -> str:
    raise NotImplementedError("Phase 6")
