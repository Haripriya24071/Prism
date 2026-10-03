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
