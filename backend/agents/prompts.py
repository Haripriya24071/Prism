"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from typing import TYPE_CHECKING, Any
try:
    import structlog  # type: ignore[import-not-found, import-untyped]
    logger: Any = structlog.get_logger()
except ImportError:
    import logging

    class _FallbackLogger:
        """Fallback adapter providing structlog-compatible keyword logging via standard logging."""
        def __init__(self) -> None:
            self._logger = logging.getLogger("prism.agents.prompts")

        def info(self, event: str, **kwargs: Any) -> None:
            kw_str = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
            self._logger.info("%s %s", event, kw_str)

        def error(self, event: str, **kwargs: Any) -> None:
            kw_str = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
            self._logger.error("%s %s", event, kw_str)

        def warning(self, event: str, **kwargs: Any) -> None:
            kw_str = " ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
            self._logger.warning("%s %s", event, kw_str)

    logger = _FallbackLogger()

if TYPE_CHECKING:
    from backend.agents.personas import PERSONAS
    from backend.models.agents import AgentPersona
    from backend.models.context import ContextPackage
    from backend.models.intake import IntakePackage
else:
    try:
        from backend.agents.personas import PERSONAS
        from backend.models.agents import AgentPersona
        from backend.models.context import ContextPackage
        from backend.models.intake import IntakePackage
    except ImportError:
        from agents.personas import PERSONAS
        from models.agents import AgentPersona
        from models.context import ContextPackage
        from models.intake import IntakePackage

__all__ = ["build_agent_prompt", "_BRD_SECTIONS", "_BASE_TEMPLATE", "_build_context_block"]

_BRD_SECTIONS = [
    "Executive Summary",
    "Market Analysis",
    "Functional Requirements",
    "Technical Requirements",
    "Risk Register",
    "Go-To-Market Strategy",
]

_BASE_TEMPLATE = """You are acting as: {persona_title}
MANDATE: {persona_mandate}

YOUR HARD CONSTRAINTS:
{constraint_axes}

FOUNDER INTAKE DATA [SOURCE: founder]:
- Raw Idea: {raw_idea}
- Target Region: {region}
- Industry Vertical: {industry}
- Product Stage: {stage}
- Budget Range: {budget}
- Success Definition: {success_def}
- File Context Attached: {file_context}

REAL-WORLD CONTEXT HARVESTED:
{context_block}

TASK:
Produce structured BRD section contributions matching your persona and mandate.
Every claim, market stat, competitor name, religious factor, political risk, or regulatory mandate you mention MUST cite its source using the exact format [SOURCE: source_name].
Allowed sources: [SOURCE: newsapi], [SOURCE: worldbank], [SOURCE: crunchbase], [SOURCE: govtdata], [SOURCE: grounding], [SOURCE: geopolitics], [SOURCE: gdelt], [SOURCE: religion], [SOURCE: alphavantage], [SOURCE: forex], [SOURCE: founder].

MANDATORY REAL-WORLD GROUNDING RULES:
1. In "Market Analysis": You MUST explicitly address regional demographics, religious calendars/festivals, cultural taboos, and local consumer adoption patterns [SOURCE: religion] [SOURCE: grounding].
2. In "Risk Register": You MUST audit political party interference, government policies, currency volatility, and statutory regulatory compliance [SOURCE: geopolitics] [SOURCE: govtdata] [SOURCE: forex].
3. In "Go-To-Market Strategy": You MUST incorporate seasonal demand timing (festive shopping spikes vs. lull periods), local market sentiment, and recent news trends [SOURCE: religion] [SOURCE: alphavantage] [SOURCE: newsapi].

Return ONLY a valid JSON object mapping each of the 6 BRD sections to your enriched analysis.
Format:
{{
  "Executive Summary": "<your analysis with [SOURCE: ...] tags>",
  "Market Analysis": "<your analysis with [SOURCE: ...] tags>",
  "Functional Requirements": "<your analysis with [SOURCE: ...] tags>",
  "Technical Requirements": "<your analysis with [SOURCE: ...] tags>",
  "Risk Register": "<your analysis with [SOURCE: ...] tags>",
  "Go-To-Market Strategy": "<your analysis with [SOURCE: ...] tags>"
}}
Do NOT output markdown commentary outside the JSON."""


def _build_context_block(context: ContextPackage) -> str:
    """Formats ContextPackage into labeled sections for the prompt."""
    blocks = []

    # 1. News Articles
    if context.news_items:
        news_lines = [f"  - {item.title} ({item.source})" for item in context.news_items[:4]]
        blocks.append("[SOURCE: newsapi]\n" + "\n".join(news_lines))
    else:
        blocks.append("[SOURCE: newsapi]\n  - No news articles harvested")

    # 2. Macroeconomic Indicators
    if context.market_data:
        m = context.market_data
        m_lines = [
            f"  - GDP per Capita: ${m.gdp_per_capita_usd:,.2f}" if m.gdp_per_capita_usd is not None else "  - GDP per Capita: N/A",
            f"  - Ease of Business Rank: #{m.ease_of_doing_business_rank}" if m.ease_of_doing_business_rank is not None else "  - Ease of Business Rank: N/A",
            f"  - Inflation Rate: {m.inflation_rate_pct}%" if m.inflation_rate_pct is not None else "  - Inflation Rate: N/A",
        ]
        blocks.append("[SOURCE: worldbank]\n" + "\n".join(m_lines))
    else:
        blocks.append("[SOURCE: worldbank]\n  - No World Bank data harvested")

    # 3. Geopolitical Climate & Ruling Party Dynamics
    geo = getattr(context, "geopolitical_data", {}) or {}
    if geo:
        geo_lines = [
            f"  - Country: {geo.get('country', 'Regional')}",
            f"  - Governance System: {geo.get('political_system', 'Constitutional')}",
            f"  - Ruling Party / Coalition: {geo.get('ruling_coalition', 'Government Administration')}",
            f"  - Political Policy Priorities: {geo.get('key_political_factors', 'Digital transformation and economic growth')}",
        ]
        blocks.append("[SOURCE: geopolitics]\n" + "\n".join(geo_lines))
    else:
        blocks.append("[SOURCE: geopolitics]\n  - Stable parliamentary governance framework with active commercial oversight")

    # 4. Religious Demographics, Cultural Norms & Festive Calendars
    religion_txt = getattr(context, "religious_context", None) or geo.get("religious_demographics")
    if religion_txt:
        blocks.append(f"[SOURCE: religion]\n  - {religion_txt}")
    else:
        blocks.append("[SOURCE: religion]\n  - Multi-cultural consumer base with significant festive commercial spending surges")

    # 5. Financial Market Sentiment & Mood
    sentiment = getattr(context, "market_sentiment", {}) or {}
    if sentiment:
        score = sentiment.get("market_sentiment_score", 0.0)
        mood = sentiment.get("market_mood", "neutral").upper()
        blocks.append(f"[SOURCE: alphavantage]\n  - Market Fiscal Sentiment Mood: {mood} (Score: {score})")
    else:
        blocks.append("[SOURCE: alphavantage]\n  - Fiscal Sentiment: NEUTRAL")

    # 6. Foreign Exchange & Currency Volatility Risk
    fx = getattr(context, "forex_data", {}) or {}
    if fx:
        fx_lines = [
            f"  - Local Currency: {fx.get('currency_name')} ({fx.get('local_currency', 'USD')} {fx.get('currency_symbol', '$')})",
            f"  - Current Exchange Rate: 1 USD = {fx.get('exchange_rate_per_usd', 1.0)} {fx.get('local_currency', 'USD')}",
            f"  - Currency Volatility Exposure: {fx.get('forex_volatility_risk', 'Low')}",
        ]
        blocks.append("[SOURCE: forex]\n" + "\n".join(fx_lines))

    # 7. Venture Capital Activity
    if context.crunchbase_data:
        cb = context.crunchbase_data
        rounds = cb.get("recent_rounds", [])
        if rounds:
            cb_lines = [
                f"  - {r.get('company')}: {r.get('round')} (${r.get('amount_usd'):,} in {r.get('year')})"
                if r.get("amount_usd") is not None
                else f"  - {r.get('company')}: {r.get('round')}"
                for r in rounds[:3]
            ]
            blocks.append("[SOURCE: crunchbase]\n" + "\n".join(cb_lines))
        else:
            blocks.append("[SOURCE: crunchbase]\n  - No Crunchbase funding data harvested")
    else:
        blocks.append("[SOURCE: crunchbase]\n  - No Crunchbase funding data harvested")

    # 8. Statutory Regulatory Compliance Flags
    if context.regulatory_flags:
        reg_lines = [f"  - {flag}" for flag in context.regulatory_flags]
        blocks.append("[SOURCE: govtdata]\n" + "\n".join(reg_lines))
    else:
        blocks.append("[SOURCE: govtdata]\n  - No regional regulatory flags identified")

    # 9. Cultural Nuances & Payment Behaviors
    if context.cultural_context:
        blocks.append(f"[SOURCE: grounding]\n  - {context.cultural_context}")
    else:
        blocks.append("[SOURCE: grounding]\n  - No cultural context harvested")

    return "\n\n".join(blocks)


def build_agent_prompt(
    persona: AgentPersona,
    intake: IntakePackage,
    context: ContextPackage,
) -> str:
    """Builds a complete, source-tagged system prompt for a single agent persona.

    Never raises an exception — returns fallback prompt if formatting fails.
    """
    try:
        persona_info = PERSONAS.get(persona)
        if persona_info:
            title = persona_info["title"]
            mandate = persona_info["mandate"]
            axes = persona_info["constraint_axes"]
        else:
            title = str(persona.value)
            mandate = "Enrich the BRD with your domain expertise."
            axes = []

        axes_str = "\n".join(f"- {axis}" for axis in axes) if axes else "- None specified"

        ext = intake.extraction
        file_ctx = intake.file_context or "None"
        if len(file_ctx) > 500:
            file_ctx = file_ctx[:500] + "... [truncated]"

        context_block = _build_context_block(context)

        prompt = _BASE_TEMPLATE.format(
            persona_title=title,
            persona_mandate=mandate,
            constraint_axes=axes_str,
            brd_sections="\n".join(f"- {s}" for s in _BRD_SECTIONS),
            raw_idea=ext.raw_idea,
            region=ext.region or "Global",
            industry=ext.industry or "General",
            stage=ext.stage or "idea",
            budget=ext.budget_range or "Unspecified",
            success_def=ext.success_definition or "Unspecified",
            file_context=file_ctx,
            context_block=context_block,
        )

        sources_count = len(
            [
                s
                for s in [
                    context.news_items,
                    context.market_data,
                    context.crunchbase_data,
                    context.regulatory_flags,
                    context.cultural_context,
                ]
                if s
            ]
        )

        logger.info(
            "built_agent_prompt",
            persona=persona.value,
            prompt_chars=len(prompt),
            sources_available=sources_count,
        )
        return prompt

    except Exception as e:
        logger.error(
            "build_agent_prompt_failed",
            persona=persona.value if hasattr(persona, "value") else str(persona),
            error=str(e),
        )
        raw_idea = getattr(getattr(intake, "extraction", None), "raw_idea", "Unspecified idea")
        persona_val = persona.value if hasattr(persona, "value") else str(persona)
        return f"You are acting as {persona_val}. Analyze the product idea: {raw_idea}"
