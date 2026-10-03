"""backend/intake/document.py — Text extraction from uploaded documents."""


async def extract_document_text(file_bytes: bytes, file_type: str) -> str:
    """Extract plain text from PDF or DOCX. Max 8000 chars returned."""
    raise NotImplementedError("Phase 4")
