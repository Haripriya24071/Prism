"""backend/evaluation/merger.py — Merges top agent sections into unified BRD."""

import asyncio
import json
import time
from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix
    from backend.models.context import ContextPackage
    from backend.models.brd import MergedBRD, BRDSection, LineageTag
    from backend.errors import MergeError
    from backend.config import get_pro_model
else:
    try:
        from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix
        from backend.models.context import ContextPackage
        from backend.models.brd import MergedBRD, BRDSection, LineageTag
        from backend.errors import MergeError
        from backend.config import get_pro_model
    except ImportError:
        from models.agents import AgentOutput, AgentPersona, ScoreMatrix
        from models.context import ContextPackage
        from models.brd import MergedBRD, BRDSection, LineageTag
        from errors import MergeError
        from config import get_pro_model

logger = structlog.get_logger()

_MERGE_TIMEOUT = 90
_BRD_SECTIONS = [
    "Executive Summary",
    "Market Analysis",
    "Functional Requirements",
    "Technical Requirements",
    "Risk Register",
    "Go-To-Market Strategy",
]


def _find_best_agent_per_section(
    agent_outputs: list[AgentOutput],
    score_matrix: ScoreMatrix,
) -> dict[str, tuple[AgentPersona, str]]:
    """For each BRD section, find the agent with the highest composite score that actually has content for
    that section.

    Returns dict: section_title -> (best_persona, content_text)
    """
    best: dict[str, tuple[AgentPersona, str]] = {}

    for section in _BRD_SECTIONS:
        best_persona: AgentPersona | None = None
        best_score = -1.0
        best_content = ""

        for output in agent_outputs:
            if output.failed:
                continue
            content = output.brd_json.get(section, "")
            if not content:
                continue
            score_entry = score_matrix.scores.get(output.agent.value)
            composite = score_entry.composite if score_entry else 0.0
            if composite > best_score:
                best_score = composite
                best_persona = output.agent
                best_content = content

        if best_persona:
            best[section] = (best_persona, best_content)

    return best
