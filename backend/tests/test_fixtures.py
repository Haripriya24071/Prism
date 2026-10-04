"""backend/tests/test_fixtures.py — Unit tests verifying schema validity of all mock test fixtures."""

import json
from pathlib import Path
import pytest
from models.intake import IntakePackage
from models.agents import AgentOutput, ScoreMatrix
from models.brd import MergedBRD
from models.output import HeatmapData, InvestorScore

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "fixtures"


def test_fixtures_directory_exists():
    assert FIXTURES_DIR.exists(), f"Fixtures directory not found at {FIXTURES_DIR}"
    assert FIXTURES_DIR.is_dir()


def test_intake_package_fixture():
    path = FIXTURES_DIR / "intake_package.json"
    assert path.exists(), "intake_package.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pkg = IntakePackage.model_validate(data)
    assert pkg.session_id == "mock-session-b2b-saas-001"
    assert pkg.extraction.region == "US"
    assert pkg.extraction.industry == "Developer Tools & CyberSecurity"
    assert len(pkg.conversation_history) >= 2


@pytest.mark.parametrize("agent_name", ["vc", "lean", "cto", "ux", "regulator", "adversarial"])
def test_agent_output_fixtures(agent_name: str):
    path = FIXTURES_DIR / f"agent_{agent_name}.json"
    assert path.exists(), f"agent_{agent_name}.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    out = AgentOutput.model_validate(data)
    assert out.agent.value == agent_name
    assert not out.failed
    assert len(out.brd_json) == 6
    assert "Executive Summary" in out.brd_json
    assert "Technical Architecture" in out.brd_json


def test_score_matrix_fixture():
    path = FIXTURES_DIR / "score_matrix.json"
    assert path.exists(), "score_matrix.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    matrix = ScoreMatrix.model_validate(data)
    assert matrix.session_id == "mock-session-b2b-saas-001"
    assert len(matrix.scores) == 6
    for agent_key in ["vc", "lean", "cto", "ux", "regulator", "adversarial"]:
        assert agent_key in matrix.scores
        score = matrix.scores[agent_key]
        assert 0 <= score.composite <= 100


def test_merged_brd_fixture():
    path = FIXTURES_DIR / "merged_brd.json"
    assert path.exists(), "merged_brd.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    brd = MergedBRD.model_validate(data)
    assert brd.session_id == "mock-session-b2b-saas-001"
    assert len(brd.sections) == 6
    assert len(brd.assumptions) >= 1
    assert len(brd.failure_modes) >= 1
    assert brd.investor_readiness_score == 84


def test_heatmap_fixture():
    path = FIXTURES_DIR / "heatmap.json"
    assert path.exists(), "heatmap.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    heatmap = HeatmapData.model_validate(data)
    assert heatmap.session_id == "mock-session-b2b-saas-001"
    assert len(heatmap.bars) == 6
    for bar in heatmap.bars:
        assert 0 <= bar.risk_score <= 100


def test_investor_readiness_fixture():
    path = FIXTURES_DIR / "investor_readiness.json"
    assert path.exists(), "investor_readiness.json missing"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    investor = InvestorScore.model_validate(data)
    assert investor.session_id == "mock-session-b2b-saas-001"
    assert investor.score == 84
    assert investor.confidence_band == "fundable"
    assert len(investor.gap_flags) >= 1


def test_sse_events_fixture():
    path = FIXTURES_DIR / "sse_events.json"
    assert path.exists(), "sse_events.json missing"
    with open(path, "r", encoding="utf-8") as f:
        events = json.load(f)
    assert isinstance(events, list)
    assert len(events) >= 10
    event_names = [e.get("event") for e in events]
    assert "session_status" in event_names
    assert "context_ready" in event_names
    assert "agent_started" in event_names
    assert "agent_completed" in event_names
    assert "scores_ready" in event_names
    assert "complete" in event_names
