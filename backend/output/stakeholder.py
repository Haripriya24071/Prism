"""backend/output/stakeholder.py — Exports all 3 stakeholder PDFs to storage."""

import asyncio
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.brd import MergedBRD
    from backend.output.pdf_export import generate_pdf
    from backend.gcp.storage import write_pdf
else:
    try:
        from backend.models.brd import MergedBRD
        from backend.output.pdf_export import generate_pdf
        from backend.gcp.storage import write_pdf
    except ImportError:
        from models.brd import MergedBRD
        from output.pdf_export import generate_pdf
        from gcp.storage import write_pdf

logger = structlog.get_logger()

_VIEWS = ["investor", "technical", "regulatory"]


async def export_all_stakeholder_pdfs(
    merged_brd: MergedBRD,
    session_id: str,
) -> dict[str, str]:
    """Generates all 3 stakeholder PDFs in parallel and writes them to GCS.

    Returns dict: view -> signed GCS URL (or empty string on failure). Named output_{view}.pdf per SCHEMA.md
    — output_investor.pdf, output_technical.pdf, output_regulatory.pdf.
    """
    logger.info("stakeholder_export_start", session_id=session_id)

    async def _generate_and_upload(view: str) -> tuple[str, str]:
        try:
            pdf_bytes = await generate_pdf(merged_brd, view)  # type: ignore[arg-type]
            if not pdf_bytes:
                return view, ""
            filename = f"output_{view}.pdf"
            url = await write_pdf(session_id, filename, pdf_bytes, view)
            return view, url or ""
        except Exception as e:
            logger.warning("stakeholder_pdf_failed", view=view, error_type=type(e).__name__)
            return view, ""

    results = await asyncio.gather(
        *[_generate_and_upload(v) for v in _VIEWS],
        return_exceptions=True,
    )

    pdf_urls: dict[str, str] = {}
    for result in results:
        if isinstance(result, (Exception, BaseException)):
            logger.warning("stakeholder_gather_exception", error_type=type(result).__name__)
            continue
        view, url = result
        pdf_urls[view] = url

    logger.info(
        "stakeholder_export_complete",
        session_id=session_id,
        views_generated=sum(1 for u in pdf_urls.values() if u),
        views_failed=sum(1 for u in pdf_urls.values() if not u),
    )
    return pdf_urls
