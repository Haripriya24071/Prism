"""backend/tests/test_pure_math.py — Pure math unit tests for heatmap, investor score, and rubric."""

import pytest
from models.agents import ScoreMatrix, SectionScore, AgentPersona
from output.heatmap import calculate_heatmap, _normalise_std_to_risk
from output.investor_score import calculate_investor_score, _get_confidence_band
from evaluation.rubric import SCORING_CRITERIA


class TestNormaliseStdToRisk:
    def test_zero_std_gives_zero_risk(self) -> None:
        assert _normalise_std_to_risk(0.0) == 0

    def test_max_std_gives_100_risk(self) -> None:
        assert _normalise_std_to_risk(50.0) == 100

    def test_midpoint_std_gives_50_risk(self) -> None:
        assert _normalise_std_to_risk(25.0) == 50

    def test_output_always_in_range(self) -> None:
        for val in [0, 10, 25, 40, 50, 60, 100]:
            result = _normalise_std_to_risk(float(val))
            assert 0 <= result <= 100, f"Out of range for input {val}: {result}"


class TestCalculateHeatmap:
    def test_full_consensus_gives_zero_risk(self, sample_score_matrix: ScoreMatrix) -> None:
        # Override with full consensus scores
        scores = {
            p.value: SectionScore(
                feasibility=75,
                market_timing=75,
                regulatory_safety=75,
                user_adoption=75,
                competitive_moat=75,
                composite=75.0,
                data_citation="t",
            )
            for p in AgentPersona
        }
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_heatmap(matrix)
        assert all(b.risk_score == 0 for b in result.bars), "Full consensus must give risk=0"

    def test_max_disagreement_gives_high_risk(self) -> None:
        vals = [0, 100, 0, 100, 0, 100]
        scores = {}
        for i, p in enumerate(AgentPersona):
            v = vals[i]
            scores[p.value] = SectionScore(
                feasibility=v,
                market_timing=v,
                regulatory_safety=v,
                user_adoption=v,
                competitive_moat=v,
                composite=float(v),
                data_citation="t",
            )
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_heatmap(matrix)
        assert all(b.risk_score > 50 for b in result.bars)

    def test_returns_five_bars(self, sample_score_matrix: ScoreMatrix) -> None:
        result = calculate_heatmap(sample_score_matrix)
        assert len(result.bars) == 5

    def test_all_risk_scores_in_range(self, sample_score_matrix: ScoreMatrix) -> None:
        result = calculate_heatmap(sample_score_matrix)
        assert all(0 <= b.risk_score <= 100 for b in result.bars)

    def test_std_dev_is_float(self, sample_score_matrix: ScoreMatrix) -> None:
        result = calculate_heatmap(sample_score_matrix)
        assert all(isinstance(b.std_dev, float) for b in result.bars)

    def test_session_id_propagated(self, sample_score_matrix: ScoreMatrix) -> None:
        result = calculate_heatmap(sample_score_matrix)
        assert result.session_id == sample_score_matrix.session_id


class TestConfidenceBand:
    def test_above_70_is_fundable(self) -> None:
        assert _get_confidence_band(70) == "fundable"
        assert _get_confidence_band(100) == "fundable"

    def test_50_to_69_is_promising(self) -> None:
        assert _get_confidence_band(50) == "promising"
        assert _get_confidence_band(69) == "promising"

    def test_below_50_is_needs_work(self) -> None:
        assert _get_confidence_band(49) == "needs_work"
        assert _get_confidence_band(0) == "needs_work"


class TestCalculateInvestorScore:
    def test_high_scores_no_gaps(self, sample_score_matrix: ScoreMatrix) -> None:
        # Override with all-80 scores
        scores = {
            p.value: SectionScore(
                feasibility=80,
                market_timing=80,
                regulatory_safety=80,
                user_adoption=80,
                competitive_moat=80,
                composite=80.0,
                data_citation="t",
            )
            for p in AgentPersona
        }
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_investor_score(matrix)
        assert result.score == 80
        assert result.confidence_band == "fundable"
        assert result.gap_flags == []

    def test_low_scores_all_gaps(self) -> None:
        scores = {
            p.value: SectionScore(
                feasibility=40,
                market_timing=40,
                regulatory_safety=40,
                user_adoption=40,
                competitive_moat=40,
                composite=40.0,
                data_citation="t",
            )
            for p in AgentPersona
        }
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_investor_score(matrix)
        assert result.score == 40
        assert result.confidence_band == "needs_work"
        assert len(result.gap_flags) == 5
        assert all(f.action_item for f in result.gap_flags)

    def test_mixed_scores_correct_gaps(self) -> None:
        scores = {
            p.value: SectionScore(
                feasibility=80,
                market_timing=80,
                regulatory_safety=40,
                user_adoption=40,
                competitive_moat=80,
                composite=65.0,
                data_citation="t",
            )
            for p in AgentPersona
        }
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_investor_score(matrix)
        gap_names = [g.criterion.lower() for g in result.gap_flags]
        assert "regulatory safety" in gap_names
        assert "user adoption" in gap_names
        assert len(result.gap_flags) == 2

    def test_score_clamped_to_100(self) -> None:
        scores = {
            p.value: SectionScore(
                feasibility=100,
                market_timing=100,
                regulatory_safety=100,
                user_adoption=100,
                competitive_moat=100,
                composite=100.0,
                data_citation="t",
            )
            for p in AgentPersona
        }
        matrix = ScoreMatrix(session_id="t", scores=scores)
        result = calculate_investor_score(matrix)
        assert result.score <= 100

    def test_empty_scores_returns_zero(self) -> None:
        matrix = ScoreMatrix(session_id="t", scores={})
        result = calculate_investor_score(matrix)
        assert result.score == 0
        assert result.confidence_band == "needs_work"

    def test_session_id_propagated(self, sample_score_matrix: ScoreMatrix) -> None:
        result = calculate_investor_score(sample_score_matrix)
        assert result.session_id == sample_score_matrix.session_id


class TestRubricWeights:
    def test_weights_sum_to_one(self) -> None:
        total = sum(c["weight"] for c in SCORING_CRITERIA.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_criteria_have_description(self) -> None:
        for name, meta in SCORING_CRITERIA.items():
            assert "description" in meta, f"{name} missing description"
            assert len(meta["description"]) > 10

    def test_five_criteria(self) -> None:
        assert len(SCORING_CRITERIA) == 5
