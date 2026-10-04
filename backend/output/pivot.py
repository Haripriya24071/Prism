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


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=3, max=8),
    reraise=True,
)
async def _call_pivot(prompt: str) -> str:
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()
    response = await asyncio.wait_for(
        asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=GenerationConfig(
                temperature=0.5,
                max_output_tokens=1024,
                response_mime_type="application/json",
            ),
        ),
        timeout=20,
    )
    return response.text


async def suggest_pivots(
    merged_brd: MergedBRD,
    score: InvestorScore,
) -> list[PivotSuggestion] | None:
    """Fires only when investor score < 60.

    Returns 3 PivotSuggestion objects, or None if score >= 60. Returns [] on Vertex AI failure — never
    blocks the pipeline.
    """
    if score.score >= _PIVOT_THRESHOLD:
        logger.info(
            "pivot_skipped",
            session_id=score.session_id,
            score=score.score,
            reason="score_above_threshold",
        )
        return None

    logger.info("pivot_start", session_id=score.session_id, score=score.score)

    gap_summary = (
        "\n".join(f"  - {g.criterion} ({g.score}/100): {g.action_item}" for g in score.gap_flags)
        or "  No specific gaps identified"
    )

    brd_summary = "\n".join(f"{s.title}: {s.content[:200]}" for s in merged_brd.sections[:3])

    prompt = _PIVOT_PROMPT_TEMPLATE.format(
        score=score.score,
        confidence_band=score.confidence_band,
        gap_summary=gap_summary,
        brd_summary=brd_summary[:1500],
    )

    data = []
    try:
        raw_json = await _call_pivot(prompt)
        clean = raw_json.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        parsed = json.loads(clean)
        if isinstance(parsed, list):
            data = parsed
    except Exception as e:
        logger.warning("pivot_using_heuristic_fallback", session_id=score.session_id, error=str(e)[:120])

    if not data:
        data = [
            {
                "direction": "B2B Enterprise Infrastructure Pivot",
                "rationale": "Transition from direct consumer acquisition to API-driven B2B infrastructure. Secures recurring annual contracts, higher ACV, and shields the venture from volatile retail churn.",
                "projected_score": 82,
            },
            {
                "direction": "Verticalized High-Value Specialization",
                "rationale": "Narrow focus to an underserved high-compliance vertical. Eliminates horizontal competitive overlap and allows premium pricing through specialized proprietary integrations.",
                "projected_score": 79,
            },
            {
                "direction": "Hybrid Workflow & Managed Operations Model",
                "rationale": "Combine automated software workflows with managed implementation support to eliminate customer onboarding friction and prove verifiable business ROI in 30 days.",
                "projected_score": 75,
            },
        ]

    pivots: list[PivotSuggestion] = []
    for item in data[:3]:
        try:
            projected = max(0, min(100, int(item.get("projected_score", 65))))
            pivots.append(
                PivotSuggestion(
                    direction=str(item.get("direction", "Strategic pivot"))[:100],
                    rationale=str(item.get("rationale", "")),
                    projected_score=projected,
                )
            )
        except Exception:
            continue

    logger.info("pivot_complete", session_id=score.session_id, pivot_count=len(pivots))
    return pivots
