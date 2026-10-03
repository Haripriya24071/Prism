"""backend/agents/swarm.py — Orchestrates parallel execution of all 6 swarm agents."""

import asyncio
import json
import time
from datetime import datetime
from collections.abc import Callable, Awaitable
from typing import TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from backend.models.intake import IntakePackage
    from backend.models.context import ContextPackage
    from backend.models.agents import AgentPersona, AgentOutput
    from backend.agents.prompts import build_agent_prompt
    from backend.agents.personas import PERSONAS
    from backend.errors import SwarmError, AgentTimeoutError
    from backend.config import get_flash_model
else:
    try:
        from backend.models.intake import IntakePackage
        from backend.models.context import ContextPackage
        from backend.models.agents import AgentPersona, AgentOutput
        from backend.agents.prompts import build_agent_prompt
        from backend.agents.personas import PERSONAS
        from backend.errors import SwarmError, AgentTimeoutError
        from backend.config import get_flash_model
    except ImportError:
        from models.intake import IntakePackage
        from models.context import ContextPackage
        from models.agents import AgentPersona, AgentOutput
        from agents.prompts import build_agent_prompt
        from agents.personas import PERSONAS
        from errors import SwarmError, AgentTimeoutError
        from config import get_flash_model

logger = structlog.get_logger()

_AGENT_TIMEOUT_SECONDS = 25
_MIN_SUCCESSFUL_AGENTS = 4


def _clean_json_response(raw_text: str) -> dict:
    """Strips markdown code fences and parses JSON from raw LLM output text."""
    clean = raw_text.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        if len(parts) >= 2:
            clean = parts[1].strip()
            if clean.startswith("json"):
                clean = clean[4:].strip()
    res = json.loads(clean)
    return res if isinstance(res, dict) else {}


async def _run_single_agent(
    persona: AgentPersona,
    intake: IntakePackage,
    context: ContextPackage,
    progress_callback: Callable[[str, str], Awaitable[None]] | None = None,
) -> AgentOutput:
    """Runs one agent. Returns AgentOutput with failed=True on any error.

    Never raises — errors are captured into AgentOutput.
    """
    start = time.time()

    if progress_callback:
        try:
            await progress_callback(persona.value, "running")
        except Exception:
            pass  # progress callback failure must never kill an agent

    try:
        from vertexai.generative_models import GenerationConfig

        prompt = build_agent_prompt(persona, intake, context)
        model = get_flash_model()

        response = await asyncio.wait_for(
            asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=8192,
                ),
            ),
            timeout=_AGENT_TIMEOUT_SECONDS,
        )

        raw_text = response.text
        duration_ms = int((time.time() - start) * 1000)

        # Parse JSON BRD from response using fence stripper
        try:
            brd_json = _clean_json_response(raw_text)
        except Exception:
            logger.warning(
                "agent_json_parse_failed",
                persona=persona.value,
                duration_ms=duration_ms,
            )
            brd_json = {}

        logger.info(
            "agent_complete",
            persona=persona.value,
            duration_ms=duration_ms,
            sections_parsed=len(brd_json),
        )

        if progress_callback:
            try:
                await progress_callback(persona.value, "complete")
            except Exception:
                pass

        return AgentOutput(
            agent=persona,
            brd_json=brd_json,
            raw_text=raw_text,
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            failed=False,
        )

    except asyncio.TimeoutError:
        duration_ms = int((time.time() - start) * 1000)
        logger.error("agent_timeout", persona=persona.value, duration_ms=duration_ms)
        if progress_callback:
            try:
                await progress_callback(persona.value, "timeout")
            except Exception:
                pass
        return AgentOutput(
            agent=persona,
            brd_json={},
            raw_text="AGENT_TIMEOUT",
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            failed=True,
        )

    except Exception as e:
        duration_ms = int((time.time() - start) * 1000)
        logger.error(
            "agent_failed",
            persona=persona.value,
            duration_ms=duration_ms,
            error_type=type(e).__name__,
            # never log prompt or response content
        )
        if progress_callback:
            try:
                await progress_callback(persona.value, "error")
            except Exception:
                pass
        return AgentOutput(
            agent=persona,
            brd_json={},
            raw_text="AGENT_FAILED",
            completed_at=datetime.utcnow(),
            duration_ms=duration_ms,
            failed=True,
        )


async def _safe_write_gcs(session_id: str, filename: str, data: dict) -> None:
    """Fire-and-forget GCS writer wrapper that catches exceptions silently."""
    try:
        try:
            import backend.gcp.storage as storage_mod
        except ImportError:
            import gcp.storage as storage_mod  # type: ignore[no-redef]

        await storage_mod.write_json(session_id=session_id, filename=filename, data=data)
    except Exception as e:
        logger.warning(
            "gcs_write_failed",
            session_id=session_id,
            filename=filename,
            error_type=type(e).__name__,
        )


async def run_swarm(
    intake: IntakePackage,
    context: ContextPackage,
    session_id: str,
    progress_callback: Callable[[str, str], Awaitable[None]] | None = None,
) -> list[AgentOutput]:
    """Runs all 6 agents in parallel via asyncio.gather.

    Raises SwarmError if fewer than 4 agents succeed. Writes each successful output to GCS as a background
    task.
    """
    swarm_start = time.time()
    logger.info("swarm_start", session_id=session_id, agent_count=len(AgentPersona))

    results = await asyncio.gather(
        *[
            _run_single_agent(persona, intake, context, progress_callback)
            for persona in AgentPersona
        ],
        return_exceptions=True,
    )

    outputs: list[AgentOutput] = []
    for result in results:
        if isinstance(result, (Exception, BaseException)):
            logger.error("swarm_gather_exception", error_type=type(result).__name__)
            continue
        outputs.append(result)

    successful = [o for o in outputs if not o.failed]
    failed_count = len(outputs) - len(successful)

    swarm_elapsed_ms = int((time.time() - swarm_start) * 1000)
    logger.info(
        "swarm_complete",
        session_id=session_id,
        total=len(outputs),
        successful=len(successful),
        failed=failed_count,
        elapsed_ms=swarm_elapsed_ms,
    )

    if len(successful) < _MIN_SUCCESSFUL_AGENTS:
        raise SwarmError(
            f"Swarm produced only {len(successful)} successful agents — minimum is {_MIN_SUCCESSFUL_AGENTS}",
            detail=f"session_id={session_id}",
        )

    # Write each successful output to GCS — fire and forget
    for output in successful:
        asyncio.create_task(
            _safe_write_gcs(
                session_id=session_id,
                filename=f"agent_{output.agent.value}.json",
                data=output.model_dump(mode="json"),
            )
        )

    return outputs
