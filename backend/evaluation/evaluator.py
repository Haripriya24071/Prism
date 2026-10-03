"""backend/evaluation/evaluator.py — Scores all agent BRDs across rubric criteria."""

import asyncio
import json
import time
from typing import TYPE_CHECKING, Any
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
    from backend.models.context import ContextPackage
    from backend.errors import EvaluationError
    from backend.config import get_pro_model
    from backend.evaluation.rubric import build_rubric_prompt, SCORING_CRITERIA
else:
    try:
        from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
        from backend.models.context import ContextPackage
        from backend.errors import EvaluationError
        from backend.config import get_pro_model
        from backend.evaluation.rubric import build_rubric_prompt, SCORING_CRITERIA
    except ImportError:
        from models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
        from models.context import ContextPackage
        from errors import EvaluationError
        from config import get_pro_model
        from evaluation.rubric import build_rubric_prompt, SCORING_CRITERIA

logger = structlog.get_logger()

_EVALUATOR_TIMEOUT = 60  # Pro calls are slower — 60s timeout
_EVALUATOR_PROMPT_TEMPLATE = """You are an impartial BRD evaluator.

You have received {agent_count} Business Requirements Documents, each written by a different expert persona analysing the same business idea.

{rubric}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE SIX BRDs TO SCORE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{brds_block}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR TASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score each BRD on every criterion in the rubric.
Return a single valid JSON object. No markdown. No explanation.

Format:
{{
  "vc":          {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "composite": 0-100, "data_citation": "specific fact"}},
  "lean":        {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "composite": 0-100, "data_citation": "specific fact"}},
  "cto":         {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "composite": 0-100, "data_citation": "specific fact"}},
  "ux":          {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "competitive_moat": 0-100, "data_citation": "specific fact"}},
  "regulator":   {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "composite": 0-100, "data_citation": "specific fact"}},
  "adversarial": {{"feasibility": 0-100, "market_timing": 0-100, "regulatory_safety": 0-100, "user_adoption": 0-100, "competitive_moat": 0-100, "composite": 0-100, "data_citation": "specific fact"}}
}}

Scores must be integers 0-100. composite must equal the weighted sum using: feasibility×0.25 + market_timing×0.20 + regulatory_safety×0.20 + user_adoption×0.20 + competitive_moat×0.15."""


def _build_brds_block(agent_outputs: list[AgentOutput]) -> str:
    lines = []
    for output in agent_outputs:
        if output.failed:
            lines.append(f"[{output.agent.value.upper()}]: AGENT FAILED — skip scoring, assign 0 to all criteria")
        else:
            lines.append(f"[{output.agent.value.upper()} — {output.agent.value} persona]:")
            if output.brd_json:
                lines.append(json.dumps(output.brd_json, indent=2)[:3000])  # cap at 3000 chars per agent
            else:
                lines.append(output.raw_text[:3000])
        lines.append("")
    return "\n".join(lines)


def _clamp(value: Any, lo: int = 0, hi: int = 100) -> int:
    """Clamp a score to integer 0-100."""
    try:
        return max(lo, min(hi, int(float(value))))
    except (TypeError, ValueError):
        return 0


def _compute_composite(scores: dict[str, int]) -> float:
    weights = {k: v["weight"] for k, v in SCORING_CRITERIA.items()}
    return round(
        scores.get("feasibility", 0) * weights["feasibility"]
        + scores.get("market_timing", 0) * weights["market_timing"]
        + scores.get("regulatory_safety", 0) * weights["regulatory_safety"]
        + scores.get("user_adoption", 0) * weights["user_adoption"]
        + scores.get("competitive_moat", 0) * weights["competitive_moat"],
        2,
    )


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=2, min=5, max=20),
    reraise=True,
)
async def _call_evaluator(prompt: str) -> str:
    from vertexai.generative_models import GenerationConfig

    model = get_pro_model()
    response = await asyncio.wait_for(
        asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        ),
        timeout=_EVALUATOR_TIMEOUT,
    )
    return response.text
