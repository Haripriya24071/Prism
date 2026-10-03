"""backend/pipeline.py — End-to-end pipeline orchestrator for PRISM BRD generation."""

import asyncio
import time
from typing import TYPE_CHECKING, Any, Callable, Awaitable
import structlog

if TYPE_CHECKING:
    from backend.models.intake import IntakePackage
    from backend.models.brd import MergedBRD
    from backend.models.output import FinalOutput
    from backend.context.harvester import harvest_context
    from backend.agents.swarm import run_swarm
    from backend.agents.personas import AgentPersona
    from backend.evaluation.evaluator import evaluate_all_agents
    from backend.evaluation.merger import merge_brds
    from backend.output.heatmap import calculate_heatmap
    from backend.output.investor_score import calculate_investor_score
    from backend.output.assumptions import flag_assumptions
    from backend.output.failure_sim import extract_failure_modes
    from backend.output.pivot import suggest_pivots
    from backend.output.stakeholder import export_all_stakeholder_pdfs
    from backend.gcp.bigquery import log_run_to_bigquery
    from backend.session_store import update_session, set_session_status
    from backend.sse_manager import publish, publish_done
    from backend.errors import SwarmError
else:
    try:
        from backend.models.intake import IntakePackage
        from backend.models.brd import MergedBRD
        from backend.models.output import FinalOutput
        from backend.context.harvester import harvest_context
        from backend.agents.swarm import run_swarm
        from backend.agents.personas import AgentPersona
        from backend.evaluation.evaluator import evaluate_all_agents
        from backend.evaluation.merger import merge_brds
        from backend.output.heatmap import calculate_heatmap
        from backend.output.investor_score import calculate_investor_score
        from backend.output.assumptions import flag_assumptions
        from backend.output.failure_sim import extract_failure_modes
        from backend.output.pivot import suggest_pivots
        from backend.output.stakeholder import export_all_stakeholder_pdfs
        from backend.gcp.bigquery import log_run_to_bigquery
        from backend.session_store import update_session, set_session_status
        from backend.sse_manager import publish, publish_done
        from backend.errors import SwarmError
    except ImportError:
        from models.intake import IntakePackage
        from models.brd import MergedBRD
        from models.output import FinalOutput
        from context.harvester import harvest_context
        from agents.swarm import run_swarm
        from agents.personas import AgentPersona
        from evaluation.evaluator import evaluate_all_agents
        from evaluation.merger import merge_brds
        from output.heatmap import calculate_heatmap
        from output.investor_score import calculate_investor_score
        from output.assumptions import flag_assumptions
        from output.failure_sim import extract_failure_modes
        from output.pivot import suggest_pivots
        from output.stakeholder import export_all_stakeholder_pdfs
        from gcp.bigquery import log_run_to_bigquery
        from session_store import update_session, set_session_status
        from sse_manager import publish, publish_done
        from errors import SwarmError

logger = structlog.get_logger()


async def _make_progress_callback(session_id: str) -> Callable[[str, str], Awaitable[None]]:
    """Returns a progress_callback compatible with run_swarm signature."""
    async def callback(agent_name: str, status: str) -> None:
        agent_progress = {
            "vc": 40, "lean": 45, "cto": 50,
            "ux": 55, "regulator": 60, "adversarial": 65,
        }
        pct = agent_progress.get(agent_name, 50)
        await publish(
            session_id,
            "agent_status",
            {"agent": agent_name, "status": status},
            progress_pct=pct if status == "complete" else pct - 5,
        )
    return callback


async def run_pipeline(session_id: str, intake: IntakePackage) -> None:
    """
    Full PRISM BRD generation pipeline — runs as a FastAPI BackgroundTask.
    Publishes SSE progress events at each step.
    Updates session store with final output on completion.
    Sets session status to 'error' on unrecoverable failure.
    """
    pipeline_start = time.time()
    logger.info("pipeline_start", session_id=session_id)

    try:
        # ── Step 1: Context harvest ───────────────────────────────────
        set_session_status(session_id, "harvesting")
        await publish(session_id, "context_start", {"status": "running"}, progress_pct=10)
        context = await harvest_context(intake)
        await publish(
            session_id,
            "context_ready",
            {
                "status": "complete",
                "sources_ok": len(context.news_items) + (1 if context.market_data else 0),
            },
            progress_pct=20,
        )

        # ── Step 2: 6-agent swarm ─────────────────────────────────────
        set_session_status(session_id, "generating")
        await publish(session_id, "swarm_start", {"status": "running"}, progress_pct=25)
        progress_callback = await _make_progress_callback(session_id)

        try:
            agent_outputs = await run_swarm(intake, context, session_id, progress_callback)
        except SwarmError as e:
            logger.error("pipeline_swarm_failed", session_id=session_id, error=e.message)
            set_session_status(session_id, "error")
            update_session(session_id, error=e.message)
            await publish(session_id, "error", {"status": "error", "message": e.message}, progress_pct=0)
            await publish_done(session_id)
            return

        await publish(
            session_id,
            "swarm_complete",
            {"status": "complete", "agents": len(agent_outputs)},
            progress_pct=68,
        )

    except Exception as e:
        logger.error("pipeline_unhandled_error", session_id=session_id, error_type=type(e).__name__)
        set_session_status(session_id, "error")
        update_session(session_id, error="Pipeline failed unexpectedly")
        await publish(session_id, "error", {"status": "error", "message": "Pipeline failed"}, progress_pct=0)
        await publish_done(session_id)
