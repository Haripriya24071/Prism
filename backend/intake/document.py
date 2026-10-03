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
    """Extract plain text from PDF or DOCX. Max 8000 chars returned."""
    raise NotImplementedError("Phase 4")
