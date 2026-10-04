"""backend/output/stakeholder.py — Exports all 3 stakeholder PDFs to Cloud Storage."""

import asyncio
from typing import Literal
try:
    from backend.gcp.storage import write_pdf
    from backend.models.brd import MergedBRD
    from backend.output.pdf_export import generate_pdf
except ImportError:
    from gcp.storage import write_pdf
    from models.brd import MergedBRD
    from output.pdf_export import generate_pdf


async def export_all_stakeholder_pdfs(merged_brd: MergedBRD, session_id: str) -> dict[str, str]:
    """Generate and upload all 3 stakeholder PDFs in parallel."""
    views: list[Literal["investor", "technical", "regulatory"]] = ["investor", "technical", "regulatory"]

    async def _render_and_upload(view: Literal["investor", "technical", "regulatory"]) -> tuple[str, str]:
        pdf_bytes = await generate_pdf(merged_brd, view)
        url = await write_pdf(session_id, f"output_{view}.pdf", pdf_bytes, view=view)
        return view, url

    tasks = [_render_and_upload(v) for v in views]
    results = await asyncio.gather(*tasks)

    return dict(results)
