"""backend/evaluation/rubric.py — Weighted rubric scoring criteria constants."""

SCORING_CRITERIA: dict = {
    "feasibility":       {"weight": 0.25, "description": "Viability given stated constraints and World Bank data"},
    "market_timing":     {"weight": 0.20, "description": "Alignment with current signals from NewsAPI and Crunchbase"},
    "regulatory_safety": {"weight": 0.20, "description": "Compliance with regional law and govt open data"},
    "user_adoption":     {"weight": 0.20, "description": "Adoption likelihood from cultural context and UX signals"},
    "competitive_moat":  {"weight": 0.15, "description": "Defensibility based on competitor analysis"},
}
assert abs(sum(c["weight"] for c in SCORING_CRITERIA.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


def build_rubric_prompt() -> str:
    raise NotImplementedError("Phase 7")
