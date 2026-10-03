"""backend/intake/document.py — Text extraction from uploaded documents."""

from io import BytesIO
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.errors import IntakeError, InvalidFileError
else:
    try:
        from backend.errors import IntakeError, InvalidFileError
    except ImportError:
        from errors import IntakeError, InvalidFileError

logger = structlog.get_logger()

# Magic bytes for supported formats
_PDF_MAGIC = b"%PDF"
_DOCX_MAGIC = b"PK\x03\x04"  # DOCX is a ZIP

_MAX_CHARS = 8000


def _truncate_to_sentence(text: str, max_chars: int) -> str:
    """Truncate to max_chars at the nearest sentence boundary (. ! ?)."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    for sep in (".", "!", "?"):
        idx = truncated.rfind(sep)
        if idx > max_chars // 2:
            return truncated[: idx + 1].strip()
    return truncated.strip()


async def extract_document_text(file_bytes: bytes, file_type: str) -> str:
    """Extract plain text from PDF or DOCX.

    Returns max 8000 chars truncated to nearest sentence boundary. Raises InvalidFileError on wrong
    magic bytes or parse failure.
    """
    if len(file_bytes) == 0:
        raise InvalidFileError("Uploaded file is empty")

    if file_type == "pdf":
        if not file_bytes.startswith(_PDF_MAGIC):
            raise InvalidFileError("File does not appear to be a valid PDF")
        try:
            from PyPDF2 import PdfReader  # source-driven-development: PdfReader not PdfFileReader

            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            raw = "\n".join(pages)
        except Exception as e:
            logger.warning("pdf_parse_failed", error_type=type(e).__name__)
            raise IntakeError("Could not extract text from PDF", detail=str(e))

    elif file_type == "doc":
        raise NotImplementedError("DOCX extraction coming in next commit")

    else:
        raise InvalidFileError(f"Unsupported file_type: {file_type}")

    if not raw.strip():
        raise IntakeError("Document contained no extractable text")

    result = _truncate_to_sentence(raw, _MAX_CHARS)
    logger.info("document_extracted", file_type=file_type, char_count=len(result))
    return result
