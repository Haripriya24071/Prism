"""backend/output/assumptions.py — Scans BRD for hidden assumptions."""

import asyncio
import json
import logging
from typing import Optional
try:
    from backend.config import get_flash_model, settings
    from backend.models.brd import AssumptionFlag, MergedBRD
    from backend.models.context import ContextPackage
except ImportError:
    from config import get_flash_model, settings
    from models.brd import AssumptionFlag, MergedBRD
    from models.context import ContextPackage

logger = logging.getLogger(__name__)


def _extract_assumptions_rule_based(merged_brd: MergedBRD) -> list[AssumptionFlag]:
    """Deterministic fallback to extract assumptions from BRD sections."""
    flags: list[AssumptionFlag] = []
    keywords = ["assume", "assuming", "expect", "forecast", "target", "predict", "projected", "adoption"]
    
    for section in (merged_brd.sections or []):
        content = section.content or ""
        lines = content.split(".")
        for line in lines:
            line_str = line.strip()
            if any(kw in line_str.lower() for kw in keywords) and len(line_str) > 15:
                flags.append(
                    AssumptionFlag(
                        assumption=line_str[:120],
                        confidence="medium",
                        evidence=f"Extracted from {section.title}",
                        recommended_action="Validate assumption with primary user testing or historical cohort data.",
                    )
                )
            if len(flags) >= 5:
                break
        if len(flags) >= 5:
            break

    if not flags:
        flags = [
            AssumptionFlag(
                assumption="Customer acquisition cost will remain stable as marketing scale increases.",
                confidence="medium",
                evidence="Standard venture market baseline",
                recommended_action="Run initial paid ad smoke test to establish baseline CAC before scaling.",
            ),
            AssumptionFlag(
                assumption="Target users will adopt digital self-serve workflow without high-touch onboarding.",
                confidence="low",
                evidence="Regional adoption patterns",
                recommended_action="Conduct 10 guided customer interviews to test self-serve usability.",
            ),
            AssumptionFlag(
                assumption="Regulatory licensing requirements will not delay launch timelines beyond 90 days.",
                confidence="high",
                evidence="Local regulatory framework",
                recommended_action="Consult regional legal counsel on pre-licensing sandboxes.",
            ),
        ]

    return flags[:5]


def _sync_flag_assumptions_gemini(merged_brd: MergedBRD, context: ContextPackage) -> Optional[list[AssumptionFlag]]:
    """Use Gemini Flash to identify hidden assumptions in the BRD against harvested context."""
    sections_text = "\n\n".join([f"### {s.title}\n{s.content}" for s in (merged_brd.sections or [])])
    if not sections_text.strip():
        return None

    prompt = f"""You are a startup diligence expert. Analyze the following Business Requirement Document (BRD) sections and harvested market context.
Identify top 3 to 5 hidden, unvalidated, or risky assumptions.

Market Context:
- Region: {context.region}
- Industry: {context.industry}
- Macro Inflation / GDP: {context.market_data.inflation_rate_pct if context.market_data else 'N/A'}% / ${context.market_data.gdp_per_capita_usd if context.market_data else 'N/A'}
- Regulatory Flags: {', '.join(context.regulatory_flags or [])}

BRD Sections:
{sections_text[:3000]}

Return ONLY a valid JSON array of objects with keys:
[
  {{
    "assumption": "string description",
    "confidence": "high | medium | low",
    "evidence": "supporting evidence or context",
    "recommended_action": "actionable validation step"
  }}
]"""

    model = get_flash_model()
    resp = model.generate_content(prompt)
    if not resp or not resp.text:
        return None

    text = resp.text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(text)
    if isinstance(data, list):
        results: list[AssumptionFlag] = []
        for item in data:
            if isinstance(item, dict) and "assumption" in item:
                conf = str(item.get("confidence", "medium")).lower()
                if conf not in ("high", "medium", "low"):
                    conf = "medium"
                results.append(
                    AssumptionFlag(
                        assumption=str(item["assumption"]),
                        confidence=conf,
                        evidence=str(item.get("evidence", "Gemini analysis")),
                        recommended_action=str(item.get("recommended_action", "Conduct market experiment")),
                    )
                )
        return results if results else None
    return None


async def flag_assumptions(merged_brd: MergedBRD, context: ContextPackage) -> list[AssumptionFlag]:
    """Flag unvalidated assumptions in the BRD using Gemini with deterministic fallback."""
    if not isinstance(merged_brd, MergedBRD) or not isinstance(context, ContextPackage):
        return _extract_assumptions_rule_based(merged_brd if isinstance(merged_brd, MergedBRD) else MergedBRD(session_id="unknown"))

    try:
        flags = await asyncio.wait_for(
            asyncio.to_thread(_sync_flag_assumptions_gemini, merged_brd, context),
            timeout=settings.EVALUATOR_TIMEOUT_SECONDS,
        )
        if flags:
            return flags
    except Exception as e:
        logger.warning("gemini_flag_assumptions_failed: %s", type(e).__name__)

    return _extract_assumptions_rule_based(merged_brd)
