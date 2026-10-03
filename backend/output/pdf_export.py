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
