"""backend/output/pivot.py — Generates pivot suggestions if score < 60."""

import asyncio
import json
from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.models.brd import MergedBRD
    from backend.models.output import InvestorScore, PivotSuggestion
    from backend.config import get_flash_model
else:
    try:
        from backend.models.brd import MergedBRD
        from backend.models.output import InvestorScore, PivotSuggestion
        from backend.config import get_flash_model
    except ImportError:
        from models.brd import MergedBRD
        from models.output import InvestorScore, PivotSuggestion
        from config import get_flash_model

logger = structlog.get_logger()

_PIVOT_THRESHOLD = 60

_PIVOT_PROMPT_TEMPLATE = """You are a startup strategy advisor.

A business idea has received an investor readiness score of {score}/100 ({confidence_band}).
The following gaps were identified:
{gap_summary}

Current BRD summary:
{brd_summary}

The score is below 60 — this idea needs a strategic pivot to become fundable.

Generate exactly 3 concrete pivot directions. Each pivot must be a meaningful strategic shift, not a cosmetic change.

Return ONLY a valid JSON array. No markdown. No explanation.
Format:
[
  {{
    "direction": "<pivot name — what fundamentally changes, 10 words max>",
    "rationale": "<why this pivot addresses the gaps — 2-3 sentences>",
    "projected_score": <integer 60-95 — realistic post-pivot investor score>
  }}
]"""
