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
