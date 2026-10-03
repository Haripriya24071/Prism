"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from typing import TYPE_CHECKING, Any
import structlog

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

logger = structlog.get_logger()

__all__ = ["build_agent_prompt", "_BRD_SECTIONS", "_BASE_TEMPLATE", "_build_context_block"]

_BRD_SECTIONS = [
    "Executive Summary",
    "Market Analysis",
    "Functional Requirements",
    "Technical Architecture",
    "Regulatory & Compliance",
    "Risk & Mitigation",
]

_BASE_TEMPLATE = """You are acting as: {persona_title}
MANDATE: {persona_mandate}

YOUR HARD CONSTRAINTS:
{constraint_axes}

BRD SECTIONS YOU ARE RESPONSIBLE FOR ENRICHING:
{brd_sections}

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
Every claim, market stat, competitor name, or regulatory risk you mention MUST cite its source using the exact format [SOURCE: source_name].
Allowed sources: [SOURCE: newsapi], [SOURCE: worldbank], [SOURCE: crunchbase], [SOURCE: govtdata], [SOURCE: grounding], [SOURCE: founder].

Respond with a clear, professional analysis covering the BRD sections assigned.
Do NOT output generic advice. Focus specifically on {raw_idea} in {region} ({industry}).
"""


def _build_context_block(context: ContextPackage) -> str:
    """Formats ContextPackage into labeled sections for the prompt."""
    blocks = []

    if context.news_items:
        news_lines = [f"  - {item.title} ({item.source})" for item in context.news_items[:3]]
        blocks.append("[SOURCE: newsapi]\n" + "\n".join(news_lines))
    else:
        blocks.append("[SOURCE: newsapi]\n  - No news articles harvested")

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

    if context.regulatory_flags:
        reg_lines = [f"  - {flag}" for flag in context.regulatory_flags]
        blocks.append("[SOURCE: govtdata]\n" + "\n".join(reg_lines))
    else:
        blocks.append("[SOURCE: govtdata]\n  - No regional regulatory flags identified")

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
