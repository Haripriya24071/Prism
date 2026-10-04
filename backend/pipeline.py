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
    from backend.preset_cache import get_cached_run, save_cached_run
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
        from backend.preset_cache import get_cached_run, save_cached_run
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
        from preset_cache import get_cached_run, save_cached_run

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
        # ── Step 0: Check Preset / Repeated Idea Cache ────────────────
        idea_text = ""
        if intake.extraction and intake.extraction.raw_idea:
            idea_text = intake.extraction.raw_idea
        elif intake.file_context:
            idea_text = intake.file_context
        elif intake.conversation_history:
            idea_text = " ".join([m.get("content", "") for m in intake.conversation_history if m.get("role") == "user"])

        cached_run = get_cached_run(idea_text)
        if cached_run:
            logger.info("pipeline_cache_hit_replay", session_id=session_id, preset_key=cached_run.get("preset_key"))
            # Fast-forward replay through progress stages so the UI stays animated without a 60s wait
            set_session_status(session_id, "harvesting")
            await publish(session_id, "context_start", {"status": "running"}, progress_pct=15)
            await asyncio.sleep(0.12)
            await publish(session_id, "context_ready", {"status": "complete", "sources_ok": 3, "geopolitics": True, "sentiment": "bullish"}, progress_pct=25)
            await asyncio.sleep(0.1)

            set_session_status(session_id, "generating")
            await publish(session_id, "swarm_start", {"status": "running"}, progress_pct=30)
            agent_names = ["vc", "lean", "cto", "ux", "regulator", "adversarial"]
            for idx, name in enumerate(agent_names, 1):
                pct = 30 + int(idx * 6)
                await publish(session_id, "agent_status", {"agent": name, "status": "running"}, progress_pct=pct - 3)
                await asyncio.sleep(0.15)
                await publish(session_id, "agent_status", {"agent": name, "status": "complete"}, progress_pct=pct)

            await publish(session_id, "swarm_complete", {"status": "complete", "agents": 6}, progress_pct=70)
            await asyncio.sleep(0.12)

            set_session_status(session_id, "evaluating")
            await publish(session_id, "evaluation_start", {"status": "running"}, progress_pct=75)
            await asyncio.sleep(0.12)
            await publish(session_id, "evaluation_complete", {"status": "complete"}, progress_pct=85)

            set_session_status(session_id, "merging")
            await publish(session_id, "merge_start", {"status": "running"}, progress_pct=90)
            await asyncio.sleep(0.12)

            # Update session store with cached data
            update_session(session_id, cached_run)
            set_session_status(session_id, "complete")

            # Publish brd_ready and done
            brd_dict = cached_run.get("brd") or {}
            await publish(
                session_id,
                "brd_ready",
                {
                    "status": "complete",
                    "investor_score": cached_run.get("investor_score") or cached_run.get("score", 74),
                    "confidence_band": cached_run.get("confidence_band", "fundable"),
                    "sections_count": len(brd_dict.get("sections", [])),
                    "sections": brd_dict.get("sections", []),
                    "brd": brd_dict,
                    "heatmap": cached_run.get("heatmap"),
                    "pivots": cached_run.get("pivots", []),
                    "agent_outputs": cached_run.get("agent_outputs", []),
                    "score_matrix": cached_run.get("score_matrix"),
                    "is_cached": True,
                },
                progress_pct=100,
            )
            await publish_done(session_id)
            logger.info("pipeline_cache_replay_complete", session_id=session_id)
            return

        # ── Step 1: Context harvest ───────────────────────────────────
        set_session_status(session_id, "harvesting")
        await publish(session_id, "context_start", {"status": "running"}, progress_pct=10)
        context = await harvest_context(intake)
        update_session(session_id, context_package=context.model_dump(mode="json"))
        await publish(
            session_id,
            "context_ready",
            {
                "status": "complete",
                "sources_ok": len(context.news_items) + (1 if context.market_data else 0),
                "geopolitics": bool(context.geopolitical_data),
                "sentiment": context.market_sentiment.get("market_mood", "neutral") if context.market_sentiment else "neutral",
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

        # ── Step 3: Evaluate ──────────────────────────────────────────
        set_session_status(session_id, "evaluating")
        await publish(session_id, "evaluation_start", {"status": "running"}, progress_pct=70)
        score_matrix = await evaluate_all_agents(agent_outputs, context)
        await publish(
            session_id,
            "evaluation_complete",
            {
                "status": "complete",
                "winning_agent": score_matrix.winning_agent.value if score_matrix.winning_agent else None,
            },
            progress_pct=80,
        )

        # ── Step 4: Merge ─────────────────────────────────────────────
        set_session_status(session_id, "merging")
        await publish(session_id, "merge_start", {"status": "running"}, progress_pct=82)
        merged_brd = await merge_brds(agent_outputs, score_matrix, context)
        await publish(session_id, "merge_complete", {"status": "complete"}, progress_pct=88)

        # ── Steps 5-8: Post-merge analysis (parallel) ─────────────────
        await publish(session_id, "analysis_start", {"status": "running"}, progress_pct=89)

        adversarial_output = next(
            (o for o in agent_outputs if o.agent == AgentPersona.ADVERSARIAL),
            None,
        )

        async def _get_failure_modes() -> list:
            if not adversarial_output:
                return []
            return await extract_failure_modes(adversarial_output)

        post_merge_results = await asyncio.gather(
            flag_assumptions(merged_brd, context),
            _get_failure_modes(),
            return_exceptions=True,
        )

        raw_assumptions = post_merge_results[0]
        raw_failures = post_merge_results[1]
        assumptions = raw_assumptions if isinstance(raw_assumptions, list) else []
        failure_modes = raw_failures if isinstance(raw_failures, list) else []

        # ── Step 9: Scores ────────────────────────────────────────────
        heatmap = calculate_heatmap(score_matrix)
        investor_score = calculate_investor_score(score_matrix)

        # Update merged BRD with investor score and analysis
        merged_brd = MergedBRD(
            session_id=merged_brd.session_id,
            sections=merged_brd.sections,
            assumptions=assumptions,
            failure_modes=failure_modes,
            investor_readiness_score=investor_score.score,
        )

        # ── Step 10: Pivot (conditional) ──────────────────────────────
        pivots = await suggest_pivots(merged_brd, investor_score)

        # ── Step 11: PDF export (background — non-blocking) ───────────
        async def _safe_export_pdfs():
            try:
                urls = await export_all_stakeholder_pdfs(merged_brd, session_id)
                update_session(session_id, pdf_urls=urls)
            except Exception as exc:
                logger.warning("pdf_export_background_failed", session_id=session_id, error=str(exc))

        asyncio.create_task(_safe_export_pdfs())

        # ── Step 12: Assemble final output ────────────────────────────
        final_output = FinalOutput(
            session_id=session_id,
            heatmap=heatmap,
            investor_score=investor_score,
            pivots=pivots or [],
        )

        # ── Step 13: Update session store ─────────────────────────────
        update_session(
            session_id,
            brd=merged_brd.model_dump(mode="json"),
            score=investor_score.score,
            status="complete",
            heatmap=heatmap.model_dump(mode="json"),
            pivots=[p.model_dump(mode="json") for p in (pivots or [])],
            investor_score=investor_score.model_dump(mode="json"),
            context=context.model_dump(mode="json") if context else None,
            context_package=context.model_dump(mode="json") if context else None,
            agent_outputs=[o.model_dump(mode="json") for o in agent_outputs],
            score_matrix=score_matrix.model_dump(mode="json"),
        )
        set_session_status(session_id, "complete")

        # ── Step 14: BigQuery logging (fire and forget) ────────────────
        pipeline_elapsed = int((time.time() - pipeline_start) * 1000)
        asyncio.create_task(
            log_run_to_bigquery(
                session_id=session_id,
                score=investor_score.score,
                duration_ms=pipeline_elapsed,
                agent_count=len([o for o in agent_outputs if not o.failed]),
            )
        )

        brd_dict = merged_brd.model_dump(mode="json")
        await publish(
            session_id,
            "brd_ready",
            {
                "status": "complete",
                "investor_score": investor_score.score,
                "confidence_band": investor_score.confidence_band,
                "sections_count": len(merged_brd.sections),
                "sections": brd_dict.get("sections", []),
                "brd": brd_dict,
                "heatmap": heatmap.model_dump(mode="json"),
                "pivots": [p.model_dump(mode="json") for p in (pivots or [])],
                "agent_outputs": [o.model_dump(mode="json") for o in agent_outputs],
                "score_matrix": score_matrix.model_dump(mode="json"),
            },
            progress_pct=100,
        )
        await publish_done(session_id)

        # ── Step 15: Save completed run to persistent cache ───────────
        try:
            idea_text = ""
            if intake.extraction and intake.extraction.raw_idea:
                idea_text = intake.extraction.raw_idea
            elif intake.file_context:
                idea_text = intake.file_context
            elif intake.conversation_history:
                idea_text = " ".join([m.get("content", "") for m in intake.conversation_history if m.get("role") == "user"])

            save_cached_run(
                idea_text,
                {
                    "status": "complete",
                    "investor_score": investor_score.score,
                    "confidence_band": investor_score.confidence_band,
                    "score": investor_score.score,
                    "sections_count": len(merged_brd.sections),
                    "sections": brd_dict.get("sections", []),
                    "brd": brd_dict,
                    "heatmap": heatmap.model_dump(mode="json"),
                    "pivots": [p.model_dump(mode="json") for p in (pivots or [])],
                    "agent_outputs": [o.model_dump(mode="json") for o in agent_outputs],
                    "score_matrix": score_matrix.model_dump(mode="json"),
                    "project_name": (intake.extraction.industry or "PRISM") + " Pitch Evaluation" if (intake.extraction and intake.extraction.industry) else "PRISM Pitch Evaluation",
                },
            )
        except Exception as cache_exc:
            logger.warning("failed_to_save_run_cache", error=str(cache_exc))

        logger.info(
            "pipeline_complete",
            session_id=session_id,
            elapsed_ms=pipeline_elapsed,
            score=investor_score.score,
        )

    except Exception as e:
        logger.error(
            "pipeline_unhandled_error",
            session_id=session_id,
            error_type=type(e).__name__,
            error=str(e),
            exc_info=True,
        )
        set_session_status(session_id, "error")
        update_session(session_id, error=f"Pipeline failed: {e}")
        await publish(session_id, "error", {"status": "error", "message": f"Pipeline failed: {e}"}, progress_pct=0)
        await publish_done(session_id)
