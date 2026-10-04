"""backend/output/pdf_export.py — Generates ReportLab PDFs for stakeholder views."""

import asyncio
import io
from typing import Literal
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
try:
    from backend.models.brd import MergedBRD
except ImportError:
    from models.brd import MergedBRD


def _sync_generate_pdf(merged_brd: MergedBRD, view: Literal["investor", "technical", "regulatory"]) -> bytes:
    """CPU-bound ReportLab PDF document builder."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Color Palette per view
    color_map = {
        "investor": HexColor("#1E3A8A"),  # Deep Navy
        "technical": HexColor("#047857"),  # Forest Emerald
        "regulatory": HexColor("#B45309"),  # Amber
    }
    primary_color = color_map.get(view, HexColor("#1E293B"))

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=HexColor("#475569"),
        spaceAfter=15,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        "BodyContent",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=HexColor("#1E293B"),
        spaceAfter=8,
    )

    lineage_style = ParagraphStyle(
        "LineageBadge",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#64748B"),
        spaceAfter=6,
    )

    story = []

    # Title & Header
    view_title_map = {
        "investor": "Investor & Commercial Evaluation View",
        "technical": "Technical Architecture & Implementation View",
        "regulatory": "Regulatory & Risk Compliance View",
    }
    story.append(Paragraph(f"PRISM — {view_title_map.get(view, 'Business Requirement Document')}", title_style))
    score_text = f" | Investor Readiness Score: <b>{merged_brd.investor_readiness_score}/100</b>" if merged_brd.investor_readiness_score is not None else ""
    story.append(Paragraph(f"Session: {merged_brd.session_id}{score_text}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=0, spaceAfter=12))

    # Sections Filtered & Prioritized by View
    sections = merged_brd.sections or []
    if view == "investor":
        # Prioritize commercial/market sections
        ordered_sections = sorted(
            sections,
            key=lambda s: 0 if any(k in s.title.lower() for k in ["market", "business", "financial", "pricing", "value"]) else 1,
        )
    elif view == "technical":
        # Prioritize technical/architecture sections
        ordered_sections = sorted(
            sections,
            key=lambda s: 0 if any(k in s.title.lower() for k in ["technical", "system", "architecture", "data", "infrastructure"]) else 1,
        )
    else:
        # Prioritize regulatory/risk sections
        ordered_sections = sorted(
            sections,
            key=lambda s: 0 if any(k in s.title.lower() for k in ["regulatory", "compliance", "legal", "risk", "security"]) else 1,
        )

    for sec in ordered_sections:
        story.append(Paragraph(sec.title, heading_style))
        if sec.lineage:
            cit = f" | Citation: {sec.lineage.data_citation}" if sec.lineage.data_citation else ""
            lineage_info = f"[Source: {sec.lineage.source_agent.value.upper()} agent | Confidence: {int(sec.lineage.confidence * 100)}%{cit}]"
            story.append(Paragraph(lineage_info, lineage_style))
        story.append(Paragraph(sec.content.replace("\n", "<br/>"), body_style))
        story.append(Spacer(1, 4))

    # Assumptions Block
    if merged_brd.assumptions:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Identified Unvalidated Assumptions", heading_style))
        for asm in merged_brd.assumptions:
            ev = f" <i>(Evidence: {asm.evidence})</i>" if asm.evidence else ""
            text = f"• <b>[{asm.confidence.upper()}]</b> {asm.assumption}{ev}<br/>&nbsp;&nbsp;<b>Action:</b> {asm.recommended_action}"
            story.append(Paragraph(text, body_style))

    # Failure Modes Block
    if merged_brd.failure_modes:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Key Risk & Failure Mode Simulations", heading_style))
        for fm in merged_brd.failure_modes:
            text = f"• <b>{fm.title} ({fm.probability_pct}% risk)</b>: {fm.description}<br/>&nbsp;&nbsp;<b>Mitigation:</b> {fm.mitigation}"
            story.append(Paragraph(text, body_style))

    doc.build(story)
    return buffer.getvalue()


async def generate_pdf(merged_brd: MergedBRD, view: Literal["investor", "technical", "regulatory"]) -> bytes:
    """Generate stakeholder PDF bytes asynchronously off the main event loop."""
    return await asyncio.to_thread(_sync_generate_pdf, merged_brd, view)
