"""backend/intake/extractor.py — Structured field extraction from conversation."""

from backend.models.intake import IntakeExtraction


async def extract_structured_fields(conversation_text: str) -> IntakeExtraction:
    """Gemini 2.0 Flash JSON-mode call. Returns structured IntakeExtraction model."""
    raise NotImplementedError("Phase 4")
