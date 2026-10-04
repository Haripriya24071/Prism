"""backend/tests/test_models.py — Unit tests for Pydantic model validations."""

from datetime import datetime
import pytest
from pydantic import ValidationError

from models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
from models.brd import BRDSection, LineageTag, MergedBRD
from models.intake import ChatRequest, IntakeExtraction, IntakePackage
from models.output import GapFlag, HeatmapBar, InvestorScore


class TestChatRequest:
    def test_valid_chat_request(self) -> None:
        r = ChatRequest(session_id="valid-id-01", message="hello", turn_number=0)
        assert r.session_id == "valid-id-01"

    def test_session_id_too_short(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(session_id="abc", message="hello", turn_number=0)

    def test_session_id_invalid_chars(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(session_id="invalid id!", message="hello", turn_number=0)

    def test_message_max_length_enforced(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(session_id="valid-id-01", message="x" * 2001, turn_number=0)

    def test_turn_number_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(session_id="valid-id-01", message="hello", turn_number=-1)


class TestIntakeExtraction:
    def test_valid_extraction(self, sample_extraction: IntakeExtraction) -> None:
        assert sample_extraction.region == "IN"
        assert sample_extraction.stage == "idea"

    def test_all_optional_fields_none(self) -> None:
        e = IntakeExtraction(raw_idea="bare idea")
        assert e.region is None
        assert e.industry is None
        assert e.stage is None

    def test_invalid_stage_rejected(self) -> None:
        with pytest.raises(ValidationError):
            IntakeExtraction(raw_idea="idea", stage="unicorn")

    def test_raw_idea_required(self) -> None:
        with pytest.raises(ValidationError):
            IntakeExtraction()  # type: ignore[call-arg]


class TestIntakePackage:
    def test_valid_intake_package(self, sample_intake: IntakePackage) -> None:
        assert sample_intake.session_id == "test-session-fixture-01"

    def test_frozen_model(self, sample_intake: IntakePackage) -> None:
        with pytest.raises(Exception):
            sample_intake.session_id = "changed"  # type: ignore[misc]

    def test_default_history_empty(self, sample_extraction: IntakeExtraction) -> None:
        pkg = IntakePackage(
            session_id="test-sess-xx",
            extraction=sample_extraction,
            created_at=datetime.utcnow(),
        )
        assert pkg.conversation_history == []


class TestAgentPersona:
    def test_all_six_personas_exist(self) -> None:
        values = {p.value for p in AgentPersona}
        assert values == {"vc", "lean", "cto", "ux", "regulator", "adversarial"}

    def test_persona_from_string(self) -> None:
        assert AgentPersona("vc") == AgentPersona.VC
        assert AgentPersona("adversarial") == AgentPersona.ADVERSARIAL

    def test_invalid_persona_raises(self) -> None:
        with pytest.raises(ValueError):
            AgentPersona("nonexistent")


class TestAgentOutput:
    def test_failed_output_defaults(self) -> None:
        out = AgentOutput(agent=AgentPersona.VC, failed=True, completed_at=datetime.utcnow())
        assert out.brd_json == {}
        assert out.raw_text == ""
        assert out.failed is True

    def test_successful_output(self, sample_agent_output_vc: AgentOutput) -> None:
        assert sample_agent_output_vc.failed is False
        assert "Executive Summary" in sample_agent_output_vc.brd_json


class TestSectionScore:
    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SectionScore(
                feasibility=150,
                market_timing=50,
                regulatory_safety=50,
                user_adoption=50,
                competitive_moat=50,
                composite=50.0,
                data_citation="t",
            )

    def test_negative_score_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SectionScore(
                feasibility=-1,
                market_timing=50,
                regulatory_safety=50,
                user_adoption=50,
                competitive_moat=50,
                composite=50.0,
                data_citation="t",
            )


class TestMergedBRD:
    def test_valid_merged_brd(self, sample_merged_brd: MergedBRD) -> None:
        assert len(sample_merged_brd.sections) == 6
        assert all(s.lineage is not None for s in sample_merged_brd.sections)

    def test_empty_sections_allowed(self) -> None:
        brd = MergedBRD(session_id="test", sections=[])
        assert brd.sections == []
        assert brd.investor_readiness_score is None

    def test_lineage_tag_confidence_range(self) -> None:
        with pytest.raises(ValidationError):
            LineageTag(source_agent=AgentPersona.VC, confidence=1.5, data_citation="t")


class TestInvestorScore:
    def test_score_range_enforced(self) -> None:
        with pytest.raises(ValidationError):
            InvestorScore(session_id="t", score=101, confidence_band="fundable")

    def test_gap_flags_default_empty(self) -> None:
        s = InvestorScore(session_id="t", score=75, confidence_band="fundable")
        assert s.gap_flags == []
