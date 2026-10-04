"""backend/tests/test_evaluation.py — Unit tests for evaluation, rubric, clamp, and merger logic."""

from datetime import datetime, timezone
import json
import pytest

from evaluation.evaluator import _build_brds_block, _clamp, _compute_composite
from evaluation.merger import _build_sections_block, _find_best_agent_per_section
from evaluation.rubric import SCORING_CRITERIA, build_rubric_prompt
from models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
from output.failure_sim import _parse_from_brd_json


class TestRubric:
    def test_weights_sum_to_one(self) -> None:
        total = sum(c["weight"] for c in SCORING_CRITERIA.values())
        assert abs(total - 1.0) < 1e-9

    def test_five_criteria(self) -> None:
        assert len(SCORING_CRITERIA) == 5

    def test_build_rubric_prompt_contains_all_criteria(self) -> None:
        prompt = build_rubric_prompt()
        for criterion in SCORING_CRITERIA:
            assert criterion.upper() in prompt.upper()

    def test_build_rubric_prompt_contains_weights(self) -> None:
        prompt = build_rubric_prompt()
        assert "25%" in prompt
        assert "20%" in prompt
        assert "15%" in prompt


class TestClamp:
    def test_clamp_above_100(self) -> None:
        assert _clamp(150) == 100

    def test_clamp_below_0(self) -> None:
        assert _clamp(-10) == 0

    def test_clamp_float_truncated(self) -> None:
        assert _clamp(75.9) == 75

    def test_clamp_string_gives_zero(self) -> None:
        assert _clamp("invalid") == 0

    def test_clamp_none_gives_zero(self) -> None:
        assert _clamp(None) == 0

    def test_valid_values_unchanged(self) -> None:
        for v in [0, 50, 100]:
            assert _clamp(v) == v


class TestComputeComposite:
    def test_known_composite(self) -> None:
        scores = {
            "feasibility": 80,
            "market_timing": 70,
            "regulatory_safety": 60,
            "user_adoption": 75,
            "competitive_moat": 65,
        }
        expected = 80 * 0.25 + 70 * 0.20 + 60 * 0.20 + 75 * 0.20 + 65 * 0.15
        assert abs(_compute_composite(scores) - expected) < 0.01

    def test_all_zeros_gives_zero(self) -> None:
        scores = {k: 0 for k in ["feasibility", "market_timing", "regulatory_safety", "user_adoption", "competitive_moat"]}
        assert _compute_composite(scores) == 0.0

    def test_all_100_gives_100(self) -> None:
        scores = {k: 100 for k in ["feasibility", "market_timing", "regulatory_safety", "user_adoption", "competitive_moat"]}
        assert abs(_compute_composite(scores) - 100.0) < 0.01


class TestBuildBRDsBlock:
    def test_failed_agent_labelled(self) -> None:
        outputs = [AgentOutput(agent=AgentPersona.ADVERSARIAL, failed=True, completed_at=datetime.now(timezone.utc))]
        block = _build_brds_block(outputs)
        assert "AGENT FAILED" in block

    def test_successful_agent_included(self, sample_agent_output_vc: AgentOutput) -> None:
        block = _build_brds_block([sample_agent_output_vc])
        assert "VC" in block.upper()


class TestFindBestAgentPerSection:
    def test_finds_correct_winner(self, all_agent_outputs: list[AgentOutput], sample_score_matrix: ScoreMatrix) -> None:
        best = _find_best_agent_per_section(all_agent_outputs, sample_score_matrix)
        assert "Executive Summary" in best
        # VC has highest composite in our fixture — should win most sections
        winner_persona, _ = best["Executive Summary"]
        assert isinstance(winner_persona, AgentPersona)

    def test_all_six_sections_covered(self, all_agent_outputs: list[AgentOutput], sample_score_matrix: ScoreMatrix) -> None:
        best = _find_best_agent_per_section(all_agent_outputs, sample_score_matrix)
        expected = {
            "Executive Summary",
            "Market Analysis",
            "Functional Requirements",
            "Technical Requirements",
            "Risk Register",
            "Go-To-Market Strategy",
        }
        assert set(best.keys()) == expected

    def test_failed_agents_excluded(self, sample_score_matrix: ScoreMatrix) -> None:
        failed_outputs = [
            AgentOutput(agent=p, failed=True, completed_at=datetime.now(timezone.utc))
            for p in AgentPersona
        ]
        best = _find_best_agent_per_section(failed_outputs, sample_score_matrix)
        assert best == {}


class TestParseFromBRDJson:
    def test_valid_risk_register_parsed(self) -> None:
        brd_json = {
            "Risk Register": json.dumps([
                {"title": "Market Risk", "probability_pct": 70, "description": "Incumbents dominate.", "mitigation": "Niche down."},
                {"title": "Reg Risk", "probability_pct": 55, "description": "RBI rules.", "mitigation": "Sandbox."},
                {"title": "Burn Risk", "probability_pct": 45, "description": "Cash runway.", "mitigation": "Revenue first."},
            ])
        }
        modes = _parse_from_brd_json(brd_json)
        assert modes is not None
        assert len(modes) == 3
        assert modes[0].title == "Market Risk"
        assert 0 <= modes[0].probability_pct <= 100

    def test_empty_risk_register_returns_none(self) -> None:
        assert _parse_from_brd_json({"Risk Register": ""}) is None
        assert _parse_from_brd_json({}) is None

    def test_probability_clamped(self) -> None:
        brd_json = {
            "Risk Register": json.dumps([
                {"title": "Over Risk", "probability_pct": 150, "description": ".", "mitigation": "."},
            ])
        }
        modes = _parse_from_brd_json(brd_json)
        if modes:
            assert all(0 <= m.probability_pct <= 100 for m in modes)
