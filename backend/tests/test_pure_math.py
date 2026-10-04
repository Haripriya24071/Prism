"""backend/tests/test_pure_math.py — Pure math unit tests for heatmap calculation."""

import pytest
from models.agents import ScoreMatrix, SectionScore, AgentPersona
from output.heatmap import calculate_heatmap, _normalise_std_to_risk


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
