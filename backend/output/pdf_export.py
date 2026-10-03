"""backend/output/pdf_export.py — Generates ReportLab PDFs."""

from typing import Literal
from backend.models.brd import MergedBRD


async def generate_pdf(merged_brd: MergedBRD, view: Literal["investor", "technical", "regulatory"]) -> bytes:
    raise NotImplementedError("Phase 9")
