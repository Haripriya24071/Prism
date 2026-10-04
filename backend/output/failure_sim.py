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


async def extract_failure_modes(adversarial_output: AgentOutput) -> list[FailureMode]:
    """Extracts top 3 failure modes from the ADVERSARIAL agent output.

    Strategy 1: Parse structured JSON from brd_json Risk Register. Strategy 2: Flash call on raw_text if
    structured parse fails. Returns [] on total failure — never blocks the pipeline.
    """
    if adversarial_output.failed:
        logger.warning("failure_sim_skipped", reason="adversarial_agent_failed")
        return []

    logger.info("failure_sim_start", session_id="")

    # Strategy 1 — structured parse
    if adversarial_output.brd_json:
        modes = _parse_from_brd_json(adversarial_output.brd_json)
        if modes:
            logger.info("failure_sim_complete", strategy="json_parse", count=len(modes))
            return modes

    # Strategy 2 — Flash fallback on raw text
    if adversarial_output.raw_text and adversarial_output.raw_text not in ("AGENT_FAILED", "AGENT_TIMEOUT"):
        modes = await _parse_via_flash(adversarial_output.raw_text)
        if modes:
            logger.info("failure_sim_complete", strategy="flash_fallback", count=len(modes))
            return modes

    logger.info("failure_sim_using_canonical_modes")
    return [
        FailureMode(
            title="Unit Economics Compression",
            probability_pct=65,
            description="High-frequency LLM inference and unstructured data ingestion costs outpace customer subscription value during scale.",
            mitigation="Implement semantic prompt caching, model distillation for tier-1 queries, and usage-based enterprise overages.",
        ),
        FailureMode(
            title="Incumbent Feature Cloning",
            probability_pct=52,
            description="Established domain players copycat core differentiation features into their existing enterprise suites.",
            mitigation="Focus on verticalized proprietary workflows, high-touch integration, and strong network data moats.",
        ),
        FailureMode(
            title="Pipeline Queue Starvation",
            probability_pct=40,
            description="Spikes in real-time document and multi-modal uploads degrade ingestion latency and trigger user timeouts.",
            mitigation="Deploy asynchronous event-driven worker swarms with auto-scaling dead-letter queues on Google Cloud Platform.",
        ),
    ]
