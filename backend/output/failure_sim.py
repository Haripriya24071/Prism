"""backend/output/failure_sim.py — Extracts failure modes from Adversarial agent output."""

import asyncio
import json
import logging
from typing import Optional
try:
    from backend.config import get_flash_model, settings
    from backend.models.agents import AgentOutput
    from backend.models.brd import FailureMode
except ImportError:
    from config import get_flash_model, settings
    from models.agents import AgentOutput
    from models.brd import FailureMode

logger = logging.getLogger(__name__)


def _default_failure_modes() -> list[FailureMode]:
    """Default fallback failure modes."""
    return [
        FailureMode(
            title="Unit Economics Collapse",
            probability_pct=45,
            description="Rising customer acquisition costs outpace user lifetime value in competitive bidding environments.",
            mitigation="Establish organic acquisition loops and enforce strict payback period caps before scaling spend.",
        ),
        FailureMode(
            title="Regulatory Enforcement Shock",
            probability_pct=35,
            description="New compliance guidelines or data residency mandates restrict core product features.",
            mitigation="Architect modular compliance layer and engage early with regional regulatory sandboxes.",
        ),
        FailureMode(
            title="Adoption Friction & High Churn",
            probability_pct=40,
            description="Target users face steep onboarding curves leading to drop-offs before reaching activation.",
            mitigation="Implement progressive disclosure in UI and instrument granular onboarding drop-off analytics.",
        ),
    ]


def _parse_from_brd_json(brd_json: dict) -> Optional[list[FailureMode]]:
    """Parse structured failure modes directly from agent's Risk Register JSON if present."""
    if not isinstance(brd_json, dict):
        return None
    raw = brd_json.get("Risk Register") or brd_json.get("risk_register")
    if not raw or not isinstance(raw, (str, list)):
        return None
    try:
        data = json.loads(raw) if isinstance(raw, str) else raw
        if isinstance(data, list) and data:
            results: list[FailureMode] = []
            for item in data:
                if isinstance(item, dict) and "title" in item:
                    try:
                        prob = int(item.get("probability_pct", 50))
                    except (ValueError, TypeError):
                        prob = 50
                    prob = max(0, min(100, prob))
                    results.append(
                        FailureMode(
                            title=str(item["title"]),
                            probability_pct=prob,
                            description=str(item.get("description", "")),
                            mitigation=str(item.get("mitigation", "")),
                        )
                    )
            return results if results else None
    except Exception:
        return None
    return None



def _sync_extract_failure_modes_gemini(text: str) -> Optional[list[FailureMode]]:
    """Use Gemini Flash to parse adversarial critiques into structured FailureMode objects."""
    prompt = f"""You are an adversarial risk auditor. Analyze the following adversarial critique of a startup venture:
Critique:
{text[:3000]}

Extract the top 3 critical failure modes.
Return ONLY a valid JSON array of objects with keys:
[
  {{
    "title": "Short punchy failure mode title",
    "probability_pct": 40,
    "description": "Detailed explanation of why and how this fails",
    "mitigation": "Clear actionable engineering or business mitigation"
  }}
]"""

    model = get_flash_model()
    resp = model.generate_content(prompt)
    if not resp or not resp.text:
        return None

    out_text = resp.text.strip()
    if out_text.startswith("```"):
        lines = out_text.splitlines()
        out_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(out_text)
    if isinstance(data, list):
        results: list[FailureMode] = []
        for item in data:
            if isinstance(item, dict) and "title" in item:
                prob = int(item.get("probability_pct", 30))
                prob = max(0, min(100, prob))
                results.append(
                    FailureMode(
                        title=str(item["title"]),
                        probability_pct=prob,
                        description=str(item.get("description", "")),
                        mitigation=str(item.get("mitigation", "")),
                    )
                )
        return results if results else None
    return None


async def extract_failure_modes(adversarial_output: AgentOutput) -> list[FailureMode]:
    """Extract failure modes from Adversarial agent output."""
    if not isinstance(adversarial_output, AgentOutput):
        return _default_failure_modes()

    raw_text = adversarial_output.raw_text or ""
    if isinstance(adversarial_output.brd_json, dict) and adversarial_output.brd_json:
        raw_text += "\n" + json.dumps(adversarial_output.brd_json)

    if not raw_text.strip():
        return _default_failure_modes()

    try:
        modes = await asyncio.wait_for(
            asyncio.to_thread(_sync_extract_failure_modes_gemini, raw_text),
            timeout=settings.EVALUATOR_TIMEOUT_SECONDS,
        )
        if modes:
            return modes
    except Exception as e:
        logger.warning("gemini_extract_failure_modes_failed: %s", type(e).__name__)

    return _default_failure_modes()
