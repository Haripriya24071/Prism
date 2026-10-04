"""backend/tests/test_intake.py — Unit tests for intake document extraction, vision, conversation, and extractor logic."""

import asyncio
import pytest
from errors import IntakeError, InvalidFileError
from intake.conversation import (
    _build_history,
    _sanitise_message,
    _detect_user_uncertainty,
    _determine_inquired_field,
    _resolve_uncertain_field,
)
from intake.document import _truncate_to_sentence, extract_document_text
from intake.extractor import _validate_region, _validate_stage
from intake.vision import analyse_image


class TestTruncateToSentence:
    def test_short_text_unchanged(self) -> None:
        text = "Hello world."
        assert _truncate_to_sentence(text, 8000) == text

    def test_truncates_at_sentence_boundary(self) -> None:
        text = "Short sentence. " * 600
        result = _truncate_to_sentence(text, 8000)
        assert len(result) <= 8000
        assert result.endswith(".")

    def test_never_exceeds_max_chars(self) -> None:
        text = "x" * 20000
        result = _truncate_to_sentence(text, 8000)
        assert len(result) <= 8000

    def test_empty_string(self) -> None:
        assert _truncate_to_sentence("", 8000) == ""


class TestExtractDocumentText:
    @pytest.mark.asyncio
    async def test_empty_bytes_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await extract_document_text(b"", "pdf")
        assert "empty" in exc.value.message.lower()

    @pytest.mark.asyncio
    async def test_bad_pdf_magic_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await extract_document_text(b"this is not a pdf", "pdf")
        assert "valid PDF" in exc.value.message

    @pytest.mark.asyncio
    async def test_bad_docx_magic_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await extract_document_text(b"not a zip", "doc")
        assert "valid DOCX" in exc.value.message

    @pytest.mark.asyncio
    async def test_unsupported_type_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await extract_document_text(b"anything", "xlsx")
        assert "Unsupported" in exc.value.message


class TestAnalyseImageValidation:
    @pytest.mark.asyncio
    async def test_empty_bytes_raises(self) -> None:
        with pytest.raises(InvalidFileError):
            await analyse_image(b"")

    @pytest.mark.asyncio
    async def test_oversized_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await analyse_image(b"x" * (11 * 1024 * 1024))
        assert "10 MB" in exc.value.message

    @pytest.mark.asyncio
    async def test_wrong_format_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            await analyse_image(b"not an image at all")
        assert "JPEG" in exc.value.message or "PNG" in exc.value.message


class TestSanitiseMessage:
    def test_strips_whitespace(self) -> None:
        assert _sanitise_message("  hello  ") == "hello"

    def test_truncates_at_2000(self) -> None:
        assert len(_sanitise_message("x" * 3000)) == 2000

    def test_empty_string_preserved(self) -> None:
        assert _sanitise_message("") == ""

    def test_normal_message_unchanged(self) -> None:
        msg = "I want to build a fintech app in India"
        assert _sanitise_message(msg) == msg


class TestBuildHistory:
    def test_empty_history(self) -> None:
        result = _build_history([])
        assert result == []

    def test_single_turn(self) -> None:
        result = _build_history([{"role": "user", "content": "hello"}])
        assert len(result) == 1

    def test_multi_turn(self) -> None:
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "model", "content": "Hi there"},
            {"role": "user", "content": "Tell me more"},
        ]
        result = _build_history(history)
        assert len(result) == 3


class TestValidateRegion:
    def test_valid_iso2_uppercase(self) -> None:
        assert _validate_region("IN") == "IN"
        assert _validate_region("US") == "US"
        assert _validate_region("GB") == "GB"

    def test_lowercase_corrected(self) -> None:
        assert _validate_region("in") == "IN"

    def test_invalid_returns_none(self) -> None:
        assert _validate_region("INDIA") is None
        assert _validate_region("123") is None
        assert _validate_region("") is None

    def test_none_input(self) -> None:
        assert _validate_region(None) is None


class TestValidateStage:
    def test_valid_stages(self) -> None:
        for stage in ["idea", "prototype", "mvp", "growth"]:
            assert _validate_stage(stage) == stage

    def test_uppercase_corrected(self) -> None:
        assert _validate_stage("MVP") == "mvp"

    def test_invalid_returns_none(self) -> None:
        assert _validate_stage("unicorn") is None
        assert _validate_stage("startup") is None

    def test_none_input(self) -> None:
        assert _validate_stage(None) is None


class TestUncertaintyHandling:
    def test_detect_user_uncertainty_phrases(self) -> None:
        phrases = [
            "I don't know",
            "i dont know",
            "No idea at all",
            "not sure about this",
            "haven't decided yet",
            "what do you recommend?",
            "you decide",
            "help me choose",
            "can't figure out",
            "dunno",
            "idk",
            "maybe",
            "whatever you think is best",
        ]
        for phrase in phrases:
            assert _detect_user_uncertainty(phrase) is True

    def test_detect_user_uncertainty_certain_phrase(self) -> None:
        assert _detect_user_uncertainty("I am building this in India for 50000 dollars") is False
        assert _detect_user_uncertainty("We have a working prototype") is False

    def test_determine_inquired_field(self) -> None:
        history = [
            {"role": "user", "content": "I want to build an invoice app"},
            {"role": "model", "content": "Where are you planning to set this up or launch first (e.g. India, US, UK)?"},
        ]
        assert _determine_inquired_field("I don't know, you decide", history, ["target region / launch country"]) == "region"

    def test_resolve_uncertain_field_region_india(self) -> None:
        field, val, rationale = _resolve_uncertain_field("region", "B2B invoicing app for kirana and MSME stores with UPI", "fintech")
        assert field == "region"
        assert val == "IN"

    def test_resolve_uncertain_field_region_us_default(self) -> None:
        field, val, rationale = _resolve_uncertain_field("region", "Cloud devops platform for kubernetes", "saas")
        assert field == "region"
        assert val == "US"

    def test_resolve_uncertain_field_stage(self) -> None:
        field, val, _ = _resolve_uncertain_field("stage", "Autonomous delivery drone", "hardware")
        assert field == "stage"
        assert val == "idea"

    def test_resolve_uncertain_field_budget(self) -> None:
        field, val, _ = _resolve_uncertain_field("budget_range", "B2B SaaS tool", "software")
        assert field == "budget_range"
        assert "Bootstrapped" in val
