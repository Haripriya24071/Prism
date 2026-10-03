"""backend/output/pdf_export.py — Generates ReportLab PDFs."""

import io
import re
from typing import Literal, TYPE_CHECKING
import structlog
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

if TYPE_CHECKING:
    from backend.models.brd import MergedBRD
else:
    try:
        from backend.models.brd import MergedBRD
    except ImportError:
        from models.brd import MergedBRD

logger = structlog.get_logger()

_VIEW_CONFIGS: dict[str, dict] = {
    "investor": {
        "title": "PRISM — Investor BRD",
        "sections": ["Executive Summary", "Market Analysis", "Go-To-Market Strategy", "Risk Register"],
        "accent_color": colors.HexColor("#7C6CFF"),
        "subtitle": "Confidential — Prepared for Investor Review",
    },
    "technical": {
        "title": "PRISM — Technical BRD",
        "sections": ["Functional Requirements", "Technical Requirements", "Risk Register", "Executive Summary"],
        "accent_color": colors.HexColor("#34D399"),
        "subtitle": "Engineering Specification Document",
    },
    "regulatory": {
        "title": "PRISM — Regulatory BRD",
        "sections": ["Risk Register", "Functional Requirements", "Executive Summary", "Go-To-Market Strategy"],
        "accent_color": colors.HexColor("#FBBF24"),
        "subtitle": "Compliance and Risk Assessment",
    },
}


def _build_styles(accent_color: colors.HexColor) -> dict:
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "PRISMTitle",
            parent=base["Title"],
            fontSize=22,
            textColor=accent_color,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "PRISMSubtitle",
            parent=base["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#888888"),
            spaceAfter=12,
        ),
        "section_heading": ParagraphStyle(
            "PRISMSection",
            parent=base["Heading1"],
            fontSize=13,
            textColor=accent_color,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "PRISMBody",
            parent=base["Normal"],
            fontSize=10,
            leading=15,
            spaceAfter=8,
        ),
        "lineage": ParagraphStyle(
            "PRISMLineage",
            parent=base["Normal"],
            fontSize=8,
            textColor=colors.HexColor("#888888"),
            spaceAfter=12,
        ),
    }
    return styles


async def generate_pdf(
    merged_brd: MergedBRD,
    view: Literal["investor", "technical", "regulatory"],
) -> bytes:
    """Generates a ReportLab PDF for one stakeholder view.

    Returns PDF as bytes. Never raises — returns empty bytes on failure.
    """
    config = _VIEW_CONFIGS.get(view, _VIEW_CONFIGS["investor"])
    styles = _build_styles(config["accent_color"])

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    story = []

    # Header
    story.append(Paragraph(config["title"], styles["title"]))
    story.append(Paragraph(config["subtitle"], styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=config["accent_color"]))
    story.append(Spacer(1, 6 * mm))

    # Session metadata
    story.append(Paragraph(f"Session ID: {merged_brd.session_id}", styles["lineage"]))
    story.append(Spacer(1, 4 * mm))

    # Sections — ordered per view config
    section_map = {s.title: s for s in merged_brd.sections}
    for section_title in config["sections"]:
        section = section_map.get(section_title)
        if not section or not section.content:
            continue

        story.append(Paragraph(section_title, styles["section_heading"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#333333")))
        story.append(Spacer(1, 2 * mm))

        # Sanitise content — remove [SOURCE:x] tags for clean PDF output
        clean_content = re.sub(r"\[SOURCE:[^\]]+\]", "", section.content).strip()
        story.append(Paragraph(clean_content or "Content not available", styles["body"]))

        if section.lineage:
            lineage_text = (
                f"Source: {section.lineage.source_agent.value} agent | Confidence:"
                f" {int(section.lineage.confidence * 100)}%"
            )
            story.append(Paragraph(lineage_text, styles["lineage"]))

        story.append(Spacer(1, 4 * mm))

    # Investor score (if available)
    if merged_brd.investor_readiness_score is not None:
        story.append(HRFlowable(width="100%", thickness=1, color=config["accent_color"]))
        story.append(Spacer(1, 4 * mm))
        story.append(
            Paragraph(
                f"Investor Readiness Score: {merged_brd.investor_readiness_score}/100",
                styles["section_heading"],
            )
        )

    try:
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        logger.info(
            "pdf_generated",
            view=view,
            size_bytes=len(pdf_bytes),
            session_id=merged_brd.session_id,
        )
        return pdf_bytes
    except Exception as e:
        logger.error("pdf_generation_failed", view=view, error_type=type(e).__name__)
        return b""
