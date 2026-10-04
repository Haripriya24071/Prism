"""backend/intake/extractor.py — Structured field extraction from conversation."""

import json
import re
from typing import cast, Literal, TYPE_CHECKING
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

StageLiteral = Literal["idea", "prototype", "mvp", "growth"]


def _validate_region(region: str | None) -> str | None:
    """Return region only if it looks like a valid ISO 3166-1 alpha-2 code."""
    if region is None:
        return None
    code = region.strip().upper()
    if _ISO2_PATTERN.match(code):
        return code
    logger.warning("invalid_region_code_ignored", raw_region=region)
    return None


def _validate_stage(stage: str | None) -> StageLiteral | None:
    """Return stage only if it is one of idea, prototype, mvp, or growth."""
    valid: set[str] = {"idea", "prototype", "mvp", "growth"}
    if stage is None or stage.lower() not in valid:
        return None
    return cast(StageLiteral, stage.lower())


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(1),
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


def _heuristic_extract(conversation_text: str) -> IntakeExtraction:
    """Resilient rule-based extraction when LLM extraction fails."""
    lower = conversation_text.lower()

    # Detect region
    region = None
    if any(k in lower for k in ["india", " in ", "in,", "in.", "delhi", "bangalore", "mumbai"]):
        region = "IN"
    elif any(k in lower for k in ["usa", "united states", "america", " us ", "us,", "california", "new york"]):
        region = "US"
    elif any(k in lower for k in ["uk", "united kingdom", "britain", "london"]):
        region = "GB"
    elif any(k in lower for k in ["europe", "germany", "france", "eu"]):
        region = "EU"

    # Detect industry
    industry = "Technology & AI"
    industries = [
        ("Fintech", ["fintech", "finance", "banking", "payment", "crypto", "defi", "lending"]),
        ("Healthcare", ["health", "medical", "doctor", "clinic", "hospital", "pharma"]),
        ("Edtech", ["edtech", "education", "learning", "student", "school", "course", "teacher"]),
        ("E-commerce", ["ecommerce", "e-commerce", "retail", "marketplace", "shop", "store"]),
        ("Logistics", ["logistics", "supply chain", "delivery", "freight", "fleet", "warehouse"]),
        ("SaaS", ["saas", "software", "b2b", "crm", "erp", "productivity", "automation"]),
    ]
    for ind_name, keywords in industries:
        if any(kw in lower for kw in keywords):
            industry = ind_name
            break

    # Detect stage
    stage: StageLiteral = "idea"
    for s in ["growth", "mvp", "prototype", "idea"]:
        if s in lower:
            stage = cast(StageLiteral, s)
            break

    # Detect budget
    budget = "Seed Stage ($25k-$50k)"
    if "bootstrapped" in lower or "bootstrap" in lower:
        budget = "Bootstrapped"
    elif any(char in lower for char in ["$", "₹", "€", "£"]):
        budget = "Funded ($50k-$250k)"

    return IntakeExtraction(
        raw_idea=conversation_text[:500].strip(),
        region=region,
        industry=industry,
        stage=stage,
        budget_range=budget,
        success_definition="Achieve product-market fit, reach initial active users, and prove unit economics within 12 months",
    )


async def extract_structured_fields(conversation_text: str) -> IntakeExtraction:
    """Single Gemini 2.0 Flash JSON-mode call with automatic heuristic fallback.

    Returns validated IntakeExtraction. Never raises.
    """
    if not conversation_text.strip():
        return IntakeExtraction(raw_idea="Unspecified project idea")

    logger.info("extraction_start", text_chars=len(conversation_text))

    data = {}
    try:
        raw_json = await _call_extraction(conversation_text)
        data = json.loads(raw_json)
    except Exception as e:
        logger.warning("extraction_using_heuristic_fallback", error=str(e)[:120])
        return _heuristic_extract(conversation_text)

    extraction = IntakeExtraction(
        raw_idea=data.get("raw_idea") or conversation_text[:500],
        region=_validate_region(data.get("region")),
        industry=data.get("industry"),
        stage=_validate_stage(data.get("stage")),
        budget_range=data.get("budget_range"),
        success_definition=data.get("success_definition"),
    )

    logger.info(
        "extraction_complete",
        region=extraction.region,
        industry=extraction.industry,
        stage=extraction.stage,
        # never log raw_idea or success_definition — user business data
    )

    return extraction
