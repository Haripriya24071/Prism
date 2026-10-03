"""backend/intake/extractor.py — Structured field extraction from conversation."""

import json
import re
from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.errors import IntakeError
    from backend.config import get_flash_model
    from backend.models.intake import IntakeExtraction
else:
    try:
        from backend.errors import IntakeError
        from backend.config import get_flash_model
        from backend.models.intake import IntakeExtraction
    except ImportError:
        from errors import IntakeError
        from config import get_flash_model
        from models.intake import IntakeExtraction

logger = structlog.get_logger()

# Valid ISO 3166-1 alpha-2 codes — basic check, not exhaustive
_ISO2_PATTERN = re.compile(r"^[A-Z]{2}$")

_EXTRACTION_PROMPT_TEMPLATE = """You are a structured data extractor.

Below is a conversation between a founder and an intake specialist.
Extract the following fields from the conversation. If a field was not mentioned, return null for that field.

Fields to extract:
- region: ISO 3166-1 alpha-2 country code (e.g. "IN", "US", "GB"). Null if not mentioned.
- industry: The industry or sector (e.g. "fintech", "edtech", "healthcare"). Null if not mentioned.
- stage: One of exactly: "idea", "prototype", "mvp", "growth". Null if not mentioned.
- budget_range: Free text budget description (e.g. "$5K-$10K", "bootstrapped", "Series A"). Null if not mentioned.
- success_definition: How the founder defines success in 12 months. Null if not mentioned.
- raw_idea: The core business idea in the founder's own words. Required — derive from conversation if not stated explicitly.

Return ONLY a valid JSON object. No explanation. No markdown. No code fences.

Conversation:
{conversation_text}"""


def _validate_region(region: str | None) -> str | None:
    """Return region only if it looks like a valid ISO 3166-1 alpha-2 code."""
    if region is None:
        return None
    code = region.strip().upper()
    if _ISO2_PATTERN.match(code):
        return code
    logger.warning("invalid_region_code_ignored", raw_region=region)
    return None


def _validate_stage(stage: str | None) -> str | None:
    """Return stage only if it is one of idea, prototype, mvp, or growth."""
    valid = {"idea", "prototype", "mvp", "growth"}
    if stage is None or stage.lower() not in valid:
        return None
    return stage.lower()


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def _call_extraction(conversation_text: str) -> str:
    """Inner retried call for Gemini 2.0 Flash JSON-mode extraction."""
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()
    prompt = _EXTRACTION_PROMPT_TEMPLATE.format(conversation_text=conversation_text)
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            temperature=0.1,  # low temp — structured extraction
            max_output_tokens=512,
            response_mime_type="application/json",
        ),
    )
    return response.text  # type: ignore[no-any-return]


async def extract_structured_fields(conversation_text: str) -> IntakeExtraction:
    """Gemini 2.0 Flash JSON-mode call. Returns structured IntakeExtraction model."""
    raise NotImplementedError("Phase 4")
