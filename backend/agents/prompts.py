"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.agents.personas import PERSONAS
    from backend.models.agents import AgentPersona
    from backend.models.context import ContextPackage
    from backend.models.intake import IntakePackage
else:
    try:
        from backend.agents.personas import PERSONAS
        from backend.models.agents import AgentPersona
        from backend.models.context import ContextPackage
        from backend.models.intake import IntakePackage
    except ImportError:
        from agents.personas import PERSONAS
        from models.agents import AgentPersona
        from models.context import ContextPackage
        from models.intake import IntakePackage

logger = structlog.get_logger()

_BRD_SECTIONS = [
    "Executive Summary",
    "Market Analysis",
    "Functional Requirements",
    "Technical Architecture",
    "Regulatory & Compliance",
    "Risk & Mitigation",
]

_BASE_TEMPLATE = """You are acting as: {persona_title}
MANDATE: {persona_mandate}

YOUR HARD CONSTRAINTS:
{constraint_axes}

BRD SECTIONS YOU ARE RESPONSIBLE FOR ENRICHING:
{brd_sections}

FOUNDER INTAKE DATA [SOURCE: founder]:
- Raw Idea: {raw_idea}
- Target Region: {region}
- Industry Vertical: {industry}
- Product Stage: {stage}
- Budget Range: {budget}
- Success Definition: {success_def}
- File Context Attached: {file_context}

REAL-WORLD CONTEXT HARVESTED:
{context_block}

TASK:
Produce structured BRD section contributions matching your persona and mandate.
Every claim, market stat, competitor name, or regulatory risk you mention MUST cite its source using the exact format [SOURCE: source_name].
Allowed sources: [SOURCE: newsapi], [SOURCE: worldbank], [SOURCE: crunchbase], [SOURCE: govtdata], [SOURCE: grounding], [SOURCE: founder].

Respond with a clear, professional analysis covering the BRD sections assigned.
Do NOT output generic advice. Focus specifically on {raw_idea} in {region} ({industry}).
"""
