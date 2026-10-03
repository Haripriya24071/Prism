"""backend/output/stakeholder.py — Exports all 3 stakeholder PDFs to storage."""

from backend.models.brd import MergedBRD


async def export_all_stakeholder_pdfs(merged_brd: MergedBRD, session_id: str) -> dict[str, str]:
    raise NotImplementedError("Phase 9")
