"""backend/context/grounding.py — Gemini Search Grounding integration client for cultural context."""

import asyncio
from backend.config import get_flash_model, init_vertex_ai
from backend.config import settings

_FALLBACK_CULTURAL_CONTEXT: dict[str, str] = {
    "in": (
        "In India, consumer adoption is heavily driven by mobile-first experiences, vernacular language support, "
        "and seamless UPI payment integrations. Trust, value sensitivity, and word-of-mouth recommendations are critical, "
        "along with compliance to data protection norms."
    ),
    "us": (
        "In the United States, users expect streamlined self-serve onboarding, clear privacy and security assurances, "
        "and integration with modern SaaS stacks. High willingness to pay is coupled with low tolerance for friction."
    ),
    "ae": (
        "In the UAE and GCC region, businesses and consumers prioritize high-touch customer support, rapid digital transformation, "
        "and alignment with regional national visions (e.g. UAE Digital Economy Strategy) and bilingual (Arabic/English) interfaces."
    ),
    "sg": (
        "In Singapore and Southeast Asia, digital-savvy users expect cross-border payment options, strong cybersecurity standards, "
        "and efficient mobile-responsive designs."
    ),
    "default": (
        "Regional market behavior emphasizes mobile responsiveness, transparent pricing, localized payment methods, "
        "and compliance with regional consumer protection standards."
    ),
}

_REGION_MAP: dict[str, str] = {
    "in": "in",
    "india": "in",
    "us": "us",
    "united states": "us",
    "usa": "us",
    "ae": "ae",
    "uae": "ae",
    "united arab emirates": "ae",
    "sg": "sg",
    "singapore": "sg",
    "gb": "default",
    "de": "default",
}


def _get_fallback(region: str) -> str:
    clean_region = region.strip().lower() if isinstance(region, str) else "default"
    canonical = _REGION_MAP.get(clean_region, "default")
    return _FALLBACK_CULTURAL_CONTEXT.get(canonical, _FALLBACK_CULTURAL_CONTEXT["default"])


def _sync_generate_grounding(region: str, industry: str) -> str:
    init_vertex_ai()
    model = get_flash_model()
    prompt = (
        f"Provide a concise 2-paragraph summary of cultural nuances, local consumer behaviors, "
        f"and market dynamics for building a {industry} venture in {region}. "
        f"Focus on actionable insights for founders and investors."
    )
    response = model.generate_content(prompt)
    if response and response.text:
        return response.text.strip()
    return _get_fallback(region)


async def fetch_gemini_grounding(region: str, industry: str) -> str:
    if not isinstance(region, str) or not isinstance(industry, str):
        return ""

    clean_region = region.strip()
    clean_industry = industry.strip()

    if not clean_region and not clean_industry:
        return _FALLBACK_CULTURAL_CONTEXT["default"]

    if not clean_region or not clean_industry:
        return ""

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_sync_generate_grounding, clean_region, clean_industry),
            timeout=settings.HARVESTER_TIMEOUT_SECONDS,
        )
    except Exception:
        return _get_fallback(clean_region)
