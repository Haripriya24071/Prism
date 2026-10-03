"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from backend.agents.personas import PERSONAS
from backend.models.agents import AgentPersona
from backend.models.context import ContextPackage
from backend.models.intake import IntakePackage


def build_agent_prompt(persona: AgentPersona, intake: IntakePackage, context: ContextPackage) -> str:
    """Builds the complete system prompt string for a given agent persona."""
    if persona not in PERSONAS:
        raise ValueError(f"Unknown or unsupported persona: {persona}")

    persona_def = PERSONAS[persona]
    title = persona_def["title"]
    mandate = persona_def["mandate"]
    constraint_axes_str = "\n".join(persona_def["constraint_axes"])

    extraction = intake.extraction
    region = extraction.region or "Unknown"
    industry = extraction.industry or "Unknown"
    stage = extraction.stage or "idea"
    raw_idea = extraction.raw_idea

    # Format top 3 news items
    news_lines = []
    for item in context.news_items[:3]:
        summary_text = item.summary or "No summary available"
        news_lines.append(f"- {item.title} ({item.source}): {summary_text}")
    news_str = "\n".join(news_lines) if news_lines else "None available"

    # Format market data
    if context.market_data:
        gdp_val = (
            f"{context.market_data.gdp_per_capita_usd:,.2f}"
            if context.market_data.gdp_per_capita_usd is not None
            else "N/A"
        )
        rank_val = (
            str(context.market_data.ease_of_doing_business_rank)
            if context.market_data.ease_of_doing_business_rank is not None
            else "N/A"
        )
        pct_val = (
            str(context.market_data.inflation_rate_pct)
            if context.market_data.inflation_rate_pct is not None
            else "N/A"
        )
    else:
        gdp_val, rank_val, pct_val = "N/A", "N/A", "N/A"

    market_str = f"GDP/capita ${gdp_val}, Ease of Business Rank #{rank_val}, Inflation {pct_val}%"

    # Format regulatory flags
    regulatory_str = ", ".join(context.regulatory_flags) if context.regulatory_flags else "None"

    # Format cultural context
    cultural_str = context.cultural_context or "None"

    # Format competitors / crunchbase data
    if context.crunchbase_data:
        competitors_str = json.dumps(context.crunchbase_data)
    else:
        competitors_str = "None available"

    prompt = f"""You are {title}. {mandate}
Your constraint axes: {constraint_axes_str}

CONTEXT YOU MUST USE:
Region: {region}
Industry: {industry}
Stage: {stage}
Idea: {raw_idea}

REAL-WORLD DATA (cite these explicitly in your output):
News: {news_str}
Market: {market_str}
Regulatory flags: {regulatory_str}
Cultural context: {cultural_str}
Competitors: {competitors_str}

OUTPUT FORMAT (JSON only, no markdown, no preamble):
{{
  "problem_statement": {{ "content": "...", "data_citation": "cite one real data point above" }},
  "functional_requirements": {{ "content": "...", "data_citation": "..." }},
  "technical_requirements": {{ "content": "...", "data_citation": "..." }},
  "risk_register": {{ "content": "...", "data_citation": "...", "failure_modes": [{{"title":"...","probability_pct":N,"description":"...","mitigation":"..."}}] }},
  "timeline_milestones": {{ "content": "...", "data_citation": "..." }},
  "assumptions": [{{"assumption":"...","confidence":"high|medium|low","evidence":"...","recommended_action":"..."}}]
}}"""

    if persona == AgentPersona.ADVERSARIAL:
        prompt += "\nAdditionally include a top-level key 'kill_shots': array of 3 objects {title, probability_pct, description, mitigation}"

    return prompt
