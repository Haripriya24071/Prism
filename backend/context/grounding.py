"""backend/context/grounding.py — Gemini Search Grounding integration client."""

from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.errors import ContextHarvestError
    from backend.config import get_flash_model
else:
    try:
        from backend.errors import ContextHarvestError
        from backend.config import get_flash_model
    except ImportError:
        from errors import ContextHarvestError
        from config import get_flash_model

logger = structlog.get_logger()

_GROUNDING_PROMPT = """You are a cultural and market intelligence analyst.

Provide a concise but specific briefing on launching a {industry} product in {region}.
Cover exactly these four areas:

1. CULTURAL CONTEXT — Key cultural values, social norms, or religious considerations that affect product adoption. Be specific to {region}, not generic.

2. SEASONAL PATTERNS — Major holidays, festivals, or seasonal cycles that affect business timing and marketing. Name specific dates or periods.

3. USER BEHAVIOUR — How people in {region} typically discover, evaluate, and adopt new {industry} products. Include payment preferences if relevant.

4. COMPETITIVE LANDSCAPE — 2-3 dominant local players in {industry} in {region} and what they do well that a new entrant must differentiate against.

Be specific and cite real patterns. Do not be generic. If you are uncertain about a detail, say so rather than fabricating."""


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=3, max=10),
    reraise=True,
)
async def _call_grounding(region: str, industry: str) -> str:
    """Inner retried call for Vertex AI Flash cultural briefing."""
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()
    prompt = _GROUNDING_PROMPT.format(region=region, industry=industry)
    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            temperature=0.3,
            max_output_tokens=1024,
        ),
    )
    return response.text  # type: ignore[no-any-return]


async def fetch_gemini_grounding(region: str, industry: str) -> str:
    """Vertex AI Flash call for cultural and market context.

    Returns plain text string. Returns empty string on failure — never blocks the pipeline.
    """
    if not region or not industry:
        logger.warning("grounding_skipped", reason="missing_region_or_industry")
        return ""

    logger.info("grounding_start", region=region, industry=industry)

    try:
        result = await _call_grounding(region, industry)
        logger.info("grounding_complete", region=region, industry=industry, response_chars=len(result))
        return result
    except Exception as e:
        logger.warning("grounding_failed", region=region, industry=industry, error_type=type(e).__name__)
        return ""
