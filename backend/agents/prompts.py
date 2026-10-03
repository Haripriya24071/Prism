"""backend/agents/prompts.py — Constructs system prompts for each agent persona."""

import json
from typing import Any
from backend.agents.personas import PERSONAS
from backend.models.agents import AgentPersona
from backend.models.context import ContextPackage
from backend.models.intake import IntakePackage

__all__ = ["build_agent_prompt"]


def _format_constraint_axes(constraint_axes: list[str]) -> str:
    """Formats persona constraint axes into a bulleted list."""
    if not constraint_axes:
        return "None specified"
    return "\n".join(f"- {axis}" for axis in constraint_axes)


def _format_news(news_items: list) -> str:
    """Formats the top 3 news items from the context package."""
    if not news_items:
        return "None available"
    lines = []
    for item in news_items[:3]:
        if isinstance(item, str):
            lines.append(f"- {item}")
            continue
        title = getattr(item, "title", None) or (item.get("title") if isinstance(item, dict) else str(item))
        source = getattr(item, "source", None) or (item.get("source") if isinstance(item, dict) else "")
        summary = getattr(item, "summary", None) or (item.get("summary") if isinstance(item, dict) else "")

        if source and summary:
            lines.append(f"- {title} ({source}): {summary}")
        elif source:
            lines.append(f"- {title} ({source})")
        elif summary:
            lines.append(f"- {title}: {summary}")
        else:
            lines.append(f"- {title}")
    return "\n".join(lines) if lines else "None available"


def _format_market_data(market_data) -> str:
    """Formats market indicators: GDP per capita, ease of business rank, and inflation rate."""
    if not market_data:
        return "None available"

    if isinstance(market_data, dict):
        gdp = market_data.get("gdp_per_capita_usd", market_data.get("gdp_usd"))
        rank = market_data.get("ease_of_doing_business_rank", market_data.get("ease_of_business_rank"))
        inflation = market_data.get("inflation_rate_pct", market_data.get("inflation_pct"))
    else:
        gdp = getattr(market_data, "gdp_per_capita_usd", None) or getattr(market_data, "gdp_usd", None)
        rank = getattr(market_data, "ease_of_doing_business_rank", None) or getattr(market_data, "ease_of_business_rank", None)
        inflation = getattr(market_data, "inflation_rate_pct", None) or getattr(market_data, "inflation_pct", None)

    gdp_val = f"${gdp:,.2f}" if gdp is not None else "N/A"
    rank_val = f"#{rank}" if rank is not None else "N/A"
    inflation_val = f"{inflation}%" if inflation is not None else "N/A"

    return f"- GDP per capita: {gdp_val}\n- Ease of Business Rank: {rank_val}\n- Inflation: {inflation_val}"


def _format_competitors(crunchbase_data) -> str:
    """Formats the top 3 competitors from Crunchbase market data."""
    if not crunchbase_data:
        return "None available"

    competitors = None
    if isinstance(crunchbase_data, dict):
        for key in ("competitors", "companies", "items", "results"):
            if key in crunchbase_data and isinstance(crunchbase_data[key], list):
                competitors = crunchbase_data[key]
                break
        if competitors is None:
            if all(isinstance(v, dict) for v in crunchbase_data.values()):
                competitors = [{"name": k, **v} for k, v in crunchbase_data.items()]
            elif all(isinstance(v, str) for v in crunchbase_data.values()):
                competitors = [f"{k}: {v}" for k, v in crunchbase_data.items()]
            else:
                competitors = [crunchbase_data]
    elif isinstance(crunchbase_data, list):
        competitors = crunchbase_data

    if not competitors:
        return "None available"

    lines = []
    for comp in competitors[:3]:
        if isinstance(comp, dict):
            name = comp.get("name", "Unknown")
            stage = comp.get("stage")
            funding = comp.get("funding")
            founded = comp.get("founded")
        elif hasattr(comp, "__dict__"):
            name = getattr(comp, "name", "Unknown")
            stage = getattr(comp, "stage", None)
            funding = getattr(comp, "funding", None)
            founded = getattr(comp, "founded", None)
        else:
            lines.append(f"- {comp}")
            continue

        details = []
        if stage:
            details.append(f"Stage: {stage}")
        if funding:
            details.append(f"Funding: {funding}")
        if founded:
            details.append(f"Founded: {founded}")
        detail_str = f" ({', '.join(details)})" if details else ""
        lines.append(f"- {name}{detail_str}")

    return "\n".join(lines) if lines else "None available"


def _format_cultural_context(cultural_context: str | None) -> str:
    """Formats the cultural context string."""
    if cultural_context and str(cultural_context).strip():
        return str(cultural_context).strip()
    return "None available"


def _format_intake_extraction(extraction) -> str:
    """Formats extracted intake fields into a readable bulleted list."""
    if isinstance(extraction, dict):
        raw_idea = extraction.get("raw_idea") or extraction.get("business_idea") or "None"
        region = extraction.get("region") or "Unknown"
        industry = extraction.get("industry") or "Unknown"
        stage = extraction.get("stage") or "idea"
        budget_range = extraction.get("budget_range") or "Not specified"
        constraints_raw = extraction.get("constraints")
    else:
        raw_idea = getattr(extraction, "raw_idea", None) or getattr(extraction, "business_idea", None) or "None"
        region = getattr(extraction, "region", None) or "Unknown"
        industry = getattr(extraction, "industry", None) or "Unknown"
        stage = getattr(extraction, "stage", None) or "idea"
        budget_range = getattr(extraction, "budget_range", None) or "Not specified"
        constraints_raw = getattr(extraction, "constraints", None)

    if isinstance(constraints_raw, list):
        constraints_str = ", ".join(str(c) for c in constraints_raw) if constraints_raw else "None specified"
    elif constraints_raw:
        constraints_str = str(constraints_raw)
    else:
        constraints_str = "None specified"

    return (
        f"- Raw Idea: {raw_idea}\n"
        f"- Region: {region}\n"
        f"- Industry: {industry}\n"
        f"- Stage: {stage}\n"
        f"- Budget Range: {budget_range}\n"
        f"- Constraints: {constraints_str}"
    )


def _get_agent_output_schema(persona: AgentPersona | None = None) -> str:
    """Builds the AgentOutput JSON schema definition string from SCHEMA.md."""
    section_template = {
        "content": "string",
        "source_agent": "vc|lean|cto|ux|regulator|adversarial",
        "confidence_score": 85,
        "data_citations": ["cite specific fact from Real-World Context above"],
        "assumptions": [
            {
                "text": "string",
                "confidence": "high|medium|low",
                "evidence": "string",
                "action": "string",
            }
        ],
    }
    schema: dict[str, Any] = {
        "problem_statement": section_template,
        "functional_requirements": section_template,
        "technical_requirements": section_template,
        "risk_register": section_template,
        "timeline_milestones": section_template,
    }
    if persona == AgentPersona.ADVERSARIAL:
        schema["kill_shots"] = [
            {
                "title": "string",
                "probability_pct": 50,
                "description": "string",
                "mitigation": "string",
            }
        ]
    return json.dumps(schema, indent=2)


def build_agent_prompt(persona: AgentPersona, intake: IntakePackage, context: ContextPackage) -> str:
    """Builds the complete system prompt string for a given agent persona."""
    if persona not in PERSONAS:
        raise ValueError(f"Unknown or unsupported persona: {persona}")

    persona_def = PERSONAS[persona]
    title = persona_def["title"]
    mandate = persona_def["mandate"]
    constraint_axes = persona_def["constraint_axes"]

    formatted_constraints = _format_constraint_axes(constraint_axes)
    formatted_news = _format_news(context.news_items)
    formatted_market_data = _format_market_data(context.market_data)
    formatted_competitors = _format_competitors(context.crunchbase_data)
    formatted_cultural = _format_cultural_context(context.cultural_context)
    formatted_idea = _format_intake_extraction(intake.extraction)
    schema_json = _get_agent_output_schema(persona)

    prompt = f"""You are {title}. Your mandate: {mandate}

## Your Hard Constraints
{formatted_constraints}

## Real-World Context
### News
{formatted_news}

### Market Data
{formatted_market_data}

### Competitors
{formatted_competitors}

### Cultural Notes
{formatted_cultural}

## The Idea
{formatted_idea}

Every data_citation must reference a specific fact from the Real-World Context above. Do not invent citations.

Respond ONLY with a valid JSON object matching this exact schema:
{schema_json}"""

    if persona == AgentPersona.ADVERSARIAL:
        prompt += "\n\nAdditionally include a top-level key 'kill_shots': array of 3 objects {title, probability_pct, description, mitigation} identifying the 3 highest-probability failure modes."

    return prompt
