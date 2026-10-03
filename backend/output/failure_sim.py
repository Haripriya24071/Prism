"""backend/output/failure_sim.py — Extracts failure modes from Adversarial agent output."""

import asyncio
import json
import re
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.agents import AgentOutput, AgentPersona
    from backend.models.brd import FailureMode
    from backend.config import get_flash_model
else:
    try:
        from backend.models.agents import AgentOutput, AgentPersona
        from backend.models.brd import FailureMode
        from backend.config import get_flash_model
    except ImportError:
        from models.agents import AgentOutput, AgentPersona
        from models.brd import FailureMode
        from config import get_flash_model

logger = structlog.get_logger()

_FALLBACK_PROMPT_TEMPLATE = """You are extracting structured failure modes from an adversarial business analysis.

RAW ANALYSIS TEXT:
{raw_text}

Extract exactly 3 failure modes from the text above.
Return ONLY a valid JSON array. No markdown. No explanation.
Format:
[
  {{
    "title": "<failure mode name — 5 words max>",
    "probability_pct": <integer 0-100>,
    "description": "<what happens and why — 2 sentences>",
    "mitigation": "<one specific countermeasure>"
  }}
]"""


def _parse_from_brd_json(brd_json: dict) -> list[FailureMode] | None:
    """Try to extract failure modes directly from the structured BRD JSON.

    Returns None if the Risk Register section does not contain parseable failure modes.
    """
    risk_text = brd_json.get("Risk Register", "")
    if not risk_text or len(risk_text) < 50:
        return None

    # Look for JSON array embedded in the risk register text
    array_match = re.search(r"\[.*?\]", risk_text, re.DOTALL)
    if array_match:
        try:
            items = json.loads(array_match.group())
            if isinstance(items, list) and len(items) > 0:
                modes = []
                for item in items[:3]:
                    modes.append(
                        FailureMode(
                            title=str(item.get("title", "Unspecified Risk"))[:50],
                            probability_pct=max(0, min(100, int(item.get("probability_pct", 50)))),
                            description=str(item.get("description", risk_text[:200])),
                            mitigation=str(item.get("mitigation", "Monitor and adapt")),
                        )
                    )
                return modes if modes else None
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
    return None


async def _parse_via_flash(raw_text: str) -> list[FailureMode]:
    """Flash fallback — parse unstructured adversarial text into FailureMode objects."""
    from vertexai.generative_models import GenerationConfig

    prompt = _FALLBACK_PROMPT_TEMPLATE.format(raw_text=raw_text[:3000])
    try:
        model = get_flash_model()
        raw_json = await asyncio.wait_for(
            asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=512,
                    response_mime_type="application/json",
                ),
            ),
            timeout=15,
        )
        clean = raw_json.text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        items = json.loads(clean)
        modes = []
        for item in items[:3]:
            modes.append(
                FailureMode(
                    title=str(item.get("title", "Failure Mode"))[:50],
                    probability_pct=max(0, min(100, int(item.get("probability_pct", 50)))),
                    description=str(item.get("description", "")),
                    mitigation=str(item.get("mitigation", "Monitor and adapt")),
                )
            )
        return modes
    except Exception as e:
        logger.warning("failure_sim_flash_fallback_failed", error_type=type(e).__name__)
        return []
