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

_MERGE_PROMPT_TEMPLATE = """You are PRISM's synthesis engine.

You have scored BRDs from 6 expert personas. Now merge them into one definitive BRD.

MERGE RULES:
1. For each of the 6 BRD sections, the best-scoring agent's version is provided below.
2. Synthesise — do not just copy. Merge the best insights from each section into one authoritative paragraph or list.
3. Preserve ALL citation tags from the source material [SOURCE: x].
4. Keep every section grounded. Remove any claim that has no [SOURCE:] tag.
5. The final BRD must be better than any individual agent's version.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEST SECTIONS BY AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{sections_block}

Return a single valid JSON object. No markdown. No explanation.
Format:
{{
  "Executive Summary":      {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Market Analysis":        {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Functional Requirements":{{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Technical Requirements": {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Risk Register":          {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Go-To-Market Strategy":  {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}}
}}"""


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


def _build_sections_block(best_per_section: dict[str, tuple[AgentPersona, str]]) -> str:
    lines = []
    for section, (persona, content) in best_per_section.items():
        lines.append(f"[{section}] — best agent: {persona.value}")
        lines.append(content[:2000])  # cap per section
        lines.append("")
    return "\n".join(lines)
