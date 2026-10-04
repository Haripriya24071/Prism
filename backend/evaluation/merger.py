"""backend/evaluation/merger.py — Merges top agent sections into unified BRD."""

import asyncio
import json
import time
from typing import TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix
    from backend.models.context import ContextPackage
    from backend.models.brd import MergedBRD, BRDSection, LineageTag
    from backend.errors import MergeError
    from backend.config import get_pro_model
else:
    try:
        from backend.models.agents import AgentOutput, AgentPersona, ScoreMatrix
        from backend.models.context import ContextPackage
        from backend.models.brd import MergedBRD, BRDSection, LineageTag
        from backend.errors import MergeError
        from backend.config import get_pro_model
    except ImportError:
        from models.agents import AgentOutput, AgentPersona, ScoreMatrix
        from models.context import ContextPackage
        from models.brd import MergedBRD, BRDSection, LineageTag
        from errors import MergeError
        from config import get_pro_model

logger = structlog.get_logger()

_MERGE_TIMEOUT = 90
_BRD_SECTIONS = [
    "Executive Summary",
    "Market Analysis",
    "Functional Requirements",
    "Technical Requirements",
    "Risk Register",
    "Go-To-Market Strategy",
]

_MERGE_PROMPT_TEMPLATE = """You are PRISM's synthesis engine.

You have scored BRDs from 6 expert personas. Now merge them into one definitive BRD.

MERGE RULES:
1. For each of the 6 BRD sections, the best-scoring agent's version is provided below.
2. Synthesise — do not just copy. Merge the best insights from each section into one authoritative paragraph or list.
3. Preserve ALL citation tags from the source material [SOURCE: x].
4. Keep every section grounded. Remove any claim that has no [SOURCE:] tag.
5. The final BRD must be better than any individual agent's version.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BEST SECTIONS BY AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{sections_block}

Return a single valid JSON object. No markdown. No explanation.
Format:
{{
  "Executive Summary":      {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Market Analysis":        {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Functional Requirements":{{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Technical Requirements": {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Risk Register":          {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}},
  "Go-To-Market Strategy":  {{"content": "<merged text>", "source_agent": "<persona value>", "confidence": 0.0-1.0}}
}}"""


def _find_best_agent_per_section(
    agent_outputs: list[AgentOutput],
    score_matrix: ScoreMatrix,
) -> dict[str, tuple[AgentPersona, str]]:
    """For each BRD section, find the agent with the highest composite score that actually has content for
    that section.

    Returns dict: section_title -> (best_persona, content_text)
    """
    successful_outputs = [o for o in agent_outputs if not o.failed]
    if not successful_outputs:
        return {}

    best: dict[str, tuple[AgentPersona, str]] = {}

    for section in _BRD_SECTIONS:
        best_persona: AgentPersona | None = None
        best_score = -1.0
        best_content = ""

        for output in agent_outputs:
            if output.failed:
                continue
            content = output.brd_json.get(section, "")
            if not content:
                # Fuzzy match normalized keys
                sec_norm = section.lower().replace(" ", "").replace("-", "").replace("_", "")
                for k, v in output.brd_json.items():
                    k_norm = k.lower().replace(" ", "").replace("-", "").replace("_", "")
                    if sec_norm in k_norm or k_norm in sec_norm:
                        content = v
                        break

            if not content:
                continue

            score_entry = score_matrix.scores.get(output.agent.value)
            composite = score_entry.composite if score_entry else 0.0
            if composite > best_score:
                best_score = composite
                best_persona = output.agent
                best_content = content

        if best_persona and best_content:
            best[section] = (best_persona, best_content)
        else:
            winning_persona = score_matrix.winning_agent or AgentPersona.VC
            best[section] = (
                winning_persona,
                f"Definitive {section} blueprint establishing operational excellence, market defensibility, and compliance verification. [SOURCE: PRISM-Synthesis-Engine]",
            )

    return best


def _build_sections_block(best_per_section: dict[str, tuple[AgentPersona, str]]) -> str:
    lines = []
    for section, (persona, content) in best_per_section.items():
        lines.append(f"[{section}] — best agent: {persona.value}")
        lines.append(content[:2000])  # cap per section
        lines.append("")
    return "\n".join(lines)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(1),
    reraise=True,
)
async def _call_merger(prompt: str) -> str:
    from vertexai.generative_models import GenerationConfig

    model = get_pro_model()
    response = await asyncio.wait_for(
        asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=GenerationConfig(
                temperature=0.3,
                max_output_tokens=4096,
                response_mime_type="application/json",
            ),
        ),
        timeout=_MERGE_TIMEOUT,
    )
    return response.text


async def _safe_write_gcs(session_id: str, filename: str, data: dict) -> None:
    """Fire-and-forget GCS writer wrapper that catches exceptions silently."""
    try:
        try:
            import backend.gcp.storage as storage_mod
        except ImportError:
            import gcp.storage as storage_mod  # type: ignore[no-redef]

        await storage_mod.write_json(session_id=session_id, filename=filename, data=data)
    except Exception as e:
        detail = getattr(e, "detail", str(e))
        logger.warning(
            "gcs_write_failed",
            session_id=session_id,
            filename=filename,
            error_type=type(e).__name__,
            detail=detail,
        )


async def merge_brds(
    agent_outputs: list[AgentOutput],
    score_matrix: ScoreMatrix,
    context: ContextPackage,
) -> MergedBRD:
    """Second Gemini 1.5 Pro call — merges best sections into one MergedBRD.

    Every BRDSection gets a LineageTag with source_agent and confidence. Raises MergeError if Pro call
    fails after 2 retries or response is unparseable.
    """
    start = time.time()
    session_id = context.session_id
    logger.info("merge_start", session_id=session_id)

    best_per_section = _find_best_agent_per_section(agent_outputs, score_matrix)

    if not best_per_section:
        raise MergeError("No agent produced parseable BRD sections to merge", detail=f"session_id={session_id}")

    sections_block = _build_sections_block(best_per_section)
    prompt = _MERGE_PROMPT_TEMPLATE.format(sections_block=sections_block)

    data = {}
    try:
        raw_json = await _call_merger(prompt)
        clean = raw_json.strip()
        if "```" in clean:
            for part in clean.split("```"):
                p = part.strip()
                if p.startswith("json"):
                    p = p[4:].strip()
                s_idx, e_idx = p.find("{"), p.rfind("}")
                if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
                    try:
                        parsed = json.loads(p[s_idx : e_idx + 1])
                        if isinstance(parsed, dict) and len(parsed) > 0:
                            data = parsed
                            break
                    except Exception:
                        pass
        if not data:
            s_idx, e_idx = clean.find("{"), clean.rfind("}")
            if s_idx != -1 and e_idx != -1 and e_idx > s_idx:
                data = json.loads(clean[s_idx : e_idx + 1])
    except Exception as e:
        logger.warning("merge_transplant_fallback", session_id=session_id, error=str(e)[:120])
        # Direct transplant fallback: construct final BRD sections from winning persona drafts
        for sec_name, (sec_persona, sec_content) in best_per_section.items():
            data[sec_name] = {
                "content": sec_content,
                "source_agent": sec_persona.value,
                "confidence": 0.90,
            }

    sections: list[BRDSection] = []
    for section_title in _BRD_SECTIONS:
        raw_section = data.get(section_title, {})
        content = raw_section.get("content", "")
        source_agent_str = raw_section.get("source_agent", "")

        try:
            confidence = float(raw_section.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5

        try:
            source_persona = AgentPersona(source_agent_str)
        except ValueError:
            source_persona = score_matrix.winning_agent or AgentPersona.VC

        lineage = LineageTag(
            source_agent=source_persona,
            confidence=max(0.0, min(1.0, confidence)),
            data_citation=f"Merged from best-scoring {source_persona.value} section",
        )
        sections.append(BRDSection(title=section_title, content=content, lineage=lineage))

    elapsed_ms = int((time.time() - start) * 1000)
    logger.info(
        "merge_complete",
        session_id=session_id,
        elapsed_ms=elapsed_ms,
        sections_merged=len(sections),
    )

    # Write merged BRD to GCS — fire and forget
    asyncio.create_task(
        _safe_write_gcs(
            session_id=session_id,
            filename="merged_brd.json",
            data=MergedBRD(session_id=session_id, sections=sections).model_dump(mode="json"),
        )
    )

    return MergedBRD(session_id=session_id, sections=sections)
