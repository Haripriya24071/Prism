"""backend/evaluation/rubric.py — Weighted rubric scoring criteria constants."""

import json

SCORING_CRITERIA: dict = {
    "feasibility":       {"weight": 0.25, "description": "Viability given stated constraints and World Bank data"},
    "market_timing":     {"weight": 0.20, "description": "Alignment with current signals from NewsAPI and Crunchbase"},
    "regulatory_safety": {"weight": 0.20, "description": "Compliance with regional law and govt open data"},
    "user_adoption":     {"weight": 0.20, "description": "Adoption likelihood from cultural context and UX signals"},
    "competitive_moat":  {"weight": 0.15, "description": "Defensibility based on competitor analysis"},
}
assert abs(sum(c["weight"] for c in SCORING_CRITERIA.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


def build_rubric_prompt() -> str:
    """Builds the scoring instruction injected into the evaluator Pro call.

    Returns a formatted string describing how to score each criterion.
    """
    lines = ["SCORING RUBRIC — apply these criteria to score each agent's BRD:"]
    lines.append("")
    for criterion, meta in SCORING_CRITERIA.items():
        weight_pct = int(meta["weight"] * 100)
        lines.append(f"  {criterion.upper()} (weight: {weight_pct}%)")
        lines.append(f"    Definition: {meta['description']}")
        lines.append(
            "    Score 0-100 where: 0=completely absent, 50=partially addressed, 100=comprehensively addressed with data citations"
        )
        lines.append("")
    lines.append("COMPOSITE SCORE = weighted sum of all five criteria using the weights above.")
    lines.append(
        "Every score must include a data_citation field proving the score with a specific fact from the BRD or context."
    )
    return "\n".join(lines)
