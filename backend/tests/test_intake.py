"""backend/tests/test_intake.py — Unit tests for intake document extraction and vision validation."""

import asyncio
import pytest
from errors import IntakeError, InvalidFileError
from intake.document import _truncate_to_sentence, extract_document_text
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
    def test_empty_bytes_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(extract_document_text(b"", "pdf"))
        assert "empty" in exc.value.message.lower()

    def test_bad_pdf_magic_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(extract_document_text(b"this is not a pdf", "pdf"))
        assert "valid PDF" in exc.value.message

    def test_bad_docx_magic_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(extract_document_text(b"not a zip", "doc"))
        assert "valid DOCX" in exc.value.message

    def test_unsupported_type_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(extract_document_text(b"anything", "xlsx"))
        assert "Unsupported" in exc.value.message


class TestAnalyseImageValidation:
    def test_empty_bytes_raises(self) -> None:
        with pytest.raises(InvalidFileError):
            asyncio.get_event_loop().run_until_complete(analyse_image(b""))

    def test_oversized_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(analyse_image(b"x" * (11 * 1024 * 1024)))
        assert "10 MB" in exc.value.message

    def test_wrong_format_raises(self) -> None:
        with pytest.raises(InvalidFileError) as exc:
            asyncio.get_event_loop().run_until_complete(analyse_image(b"not an image at all"))
        assert "JPEG" in exc.value.message or "PNG" in exc.value.message
