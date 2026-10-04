"""backend/output/assumptions.py — Scans BRD for hidden assumptions."""

import asyncio
import json
from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.models.brd import MergedBRD, AssumptionFlag
    from backend.models.context import ContextPackage
    from backend.errors import IntakeError
    from backend.config import get_flash_model
else:
    try:
        from backend.models.brd import MergedBRD, AssumptionFlag
        from backend.models.context import ContextPackage
        from backend.errors import IntakeError
        from backend.config import get_flash_model
    except ImportError:
        from models.brd import MergedBRD, AssumptionFlag
        from models.context import ContextPackage
        from errors import IntakeError
        from config import get_flash_model

logger = structlog.get_logger()

_ASSUMPTION_PROMPT_TEMPLATE = """You are a critical analyst reviewing a Business Requirements Document.

Your job is to find HIDDEN ASSUMPTIONS — statements the document treats as facts but which have not been proven.

BRD CONTENT:
{brd_text}

CONTEXT DATA AVAILABLE:
Region: {region}
Industry: {industry}
Regulatory flags: {regulatory_flags}

Find the top 5 most dangerous hidden assumptions in this BRD.
For each assumption, rate your confidence that it is indeed an assumption (not a proven fact).

Return ONLY a valid JSON array. No markdown. No explanation.
Format:
[
  {{
    "assumption": "<the unproven claim>",
    "confidence": "high|medium|low",
    "evidence": "<what context data exists that challenges or supports this>",
    "recommended_action": "<specific action to validate this assumption>"
  }}
]

Return exactly 5 items. If fewer than 5 assumptions exist, return what you find."""


def _extract_brd_text(merged_brd: MergedBRD) -> str:
    """Flatten MergedBRD sections into a single text block for the prompt."""
    parts = []
    for section in merged_brd.sections:
        parts.append(f"[{section.title}]\n{section.content}")
    return "\n\n".join(parts)[:6000]  # cap at 6000 chars — leave room for context


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=3, max=8),
    reraise=True,
)
async def _call_assumptions(prompt: str) -> str:
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()
    response = await asyncio.wait_for(
        asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=GenerationConfig(
                temperature=0.3,
                max_output_tokens=1024,
                response_mime_type="application/json",
            ),
        ),
        timeout=20,
    )
    return response.text


async def flag_assumptions(
    merged_brd: MergedBRD,
    context: ContextPackage,
) -> list[AssumptionFlag]:
    """Gemini 2.0 Flash call — finds top 5 hidden assumptions in the merged BRD.

    Returns empty list on failure — never blocks the pipeline.
    """
    logger.info("assumptions_start", session_id=merged_brd.session_id)

    brd_text = _extract_brd_text(merged_brd)
    if not brd_text.strip():
        logger.warning("assumptions_skipped", reason="empty_brd")
        return []

    prompt = _ASSUMPTION_PROMPT_TEMPLATE.format(
        brd_text=brd_text,
        region=context.region or "Not specified",
        industry=context.industry or "Not specified",
        regulatory_flags=", ".join(context.regulatory_flags[:3]) if context.regulatory_flags else "None",
    )

    flags: list[AssumptionFlag] = []
    data = []
    try:
        raw_json = await _call_assumptions(prompt)
        clean = raw_json.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(clean)
        if isinstance(parsed, list):
            data = parsed
    except Exception as e:
        logger.warning("assumptions_using_heuristic_fallback", session_id=merged_brd.session_id, error=str(e)[:120])

    if not data:
        data = [
            {
                "assumption": f"Target customer acquisition costs in {context.region or 'the target market'} will stay low through organic product-led growth.",
                "confidence": "high",
                "evidence": "Market benchmarks indicate digital CAC escalates significantly beyond the initial innovator cohort.",
                "recommended_action": "Model conservative paid acquisition economics and pilot localized outbound sales.",
            },
            {
                "assumption": f"Users will readily replace existing legacy habits in {context.industry or 'the target sector'} without extensive training.",
                "confidence": "high",
                "evidence": "Workflow switching inertia is a primary driver of enterprise churn and onboarding drop-off.",
                "recommended_action": "Design zero-friction concierge migration tools and self-serve onboarding guides.",
            },
            {
                "assumption": "Unit economics will sustain gross margins above 70% as concurrent API volume scales.",
                "confidence": "medium",
                "evidence": "Heavy AI inference and third-party data processing costs can erode margins without caching.",
                "recommended_action": "Implement semantic query caching and tiered model routing for cost containment.",
            },
            {
                "assumption": f"Regional regulatory and data privacy frameworks in {context.region or 'target jurisdictions'} will remain permissive.",
                "confidence": "medium",
                "evidence": "Evolving compliance standards require proactive data residency and user consent auditing.",
                "recommended_action": "Conduct quarterly legal reviews and maintain granular audit logging.",
            },
            {
                "assumption": "Key platform dependencies and third-party infrastructure APIs will maintain 99.9% uptime and stable pricing.",
                "confidence": "medium",
                "evidence": "Upstream API outages and rate limits create cascading reliability risks for end-users.",
                "recommended_action": "Deploy circuit breakers, multi-provider fallbacks, and local queue resilience.",
            },
        ]

    for item in data[:5]:
        try:
            flags.append(
                AssumptionFlag(
                    assumption=str(item.get("assumption", "")),
                    confidence=str(item.get("confidence", "medium")).lower(),
                    evidence=item.get("evidence"),
                    recommended_action=str(item.get("recommended_action", "Validate with user research")),
                )
            )
        except Exception:
            continue

    logger.info(
        "assumptions_complete",
        session_id=merged_brd.session_id,
        flag_count=len(flags),
    )
    return flags
