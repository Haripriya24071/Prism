"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from typing import TYPE_CHECKING
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
