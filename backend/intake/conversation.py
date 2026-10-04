"""backend/intake/conversation.py — Conversational intake turn handler with dynamic follow-up questions."""

import asyncio
import json
from typing import Any, TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.errors import IntakeError
    from backend.config import get_flash_model
    from backend.intake.extractor import extract_structured_fields
else:
    try:
        from backend.errors import IntakeError
        from backend.config import get_flash_model
        from backend.intake.extractor import extract_structured_fields
    except ImportError:
        from errors import IntakeError
        from config import get_flash_model
        from intake.extractor import extract_structured_fields

logger = structlog.get_logger()

_MAX_TURNS = 10
_MAX_MSG_LEN = 2000

_INTAKE_SYSTEM_PROMPT = """You are PRISM's venture intake specialist. Your job is to extract business parameters through a warm, concise conversation.

Rules:
- Ask exactly ONE follow-up question per turn. Never ask multiple questions or write long essays.
- Keep your reply under 3 sentences total.
- In 1 sentence, acknowledge what the founder shared.
- In 1 sentence, ask ONE sharp follow-up question focusing on what is still missing.
- Once you have all 6 core parameters, output this exact token on its own line: INTAKE_COMPLETE
- Never fabricate information the user has not provided."""


def _sanitise_message(message: str) -> str:
    """Strip whitespace, enforce max length."""
    return message.strip()[:_MAX_MSG_LEN]


def _build_history(raw_history: list[dict[str, Any]]) -> list[Any]:
    """Convert plain dicts to Vertex AI Content objects."""
    from vertexai.generative_models import Content, Part

    contents = []
    for turn in raw_history:
        role = turn.get("role", "user")
        text = turn.get("content", "")
        contents.append(Content(role=role, parts=[Part.from_text(text)]))
    return contents


def _get_suggested_chips(next_missing: str) -> list[str]:
    """Returns contextual quick-reply chips for zero-friction user responses."""
    lower = next_missing.lower()
    if "region" in lower or "country" in lower:
        return ["🇮🇳 India", "🇺🇸 United States", "🇬🇧 United Kingdom", "🇦🇪 UAE / Middle East", "🇪🇺 Europe", "🌐 Global"]
    elif "stage" in lower or "idea" in lower or "prototype" in lower:
        return ["💡 Fresh Idea", "🛠️ Early Prototype", "🚀 Active MVP", "📈 Scaling Startup"]
    elif "budget" in lower or "income" in lower:
        return ["🌱 Bootstrapped (<$15k)", "💼 Seed ($25k-$50k)", "🚀 Funded ($100k+)", "🔄 Self-funding from revenue"]
    elif "success" in lower or "milestone" in lower:
        return ["💰 $50k ARR Revenue", "👥 1,000 Active Users", "🤝 5 Enterprise Pilots", "📈 Break-even Unit Economics"]
    elif "industry" in lower or "business" in lower:
        return ["💳 Fintech / Payments", "🏥 HealthTech", "🛒 E-Commerce / Retail", "📦 Logistics & Fleet", "🤖 B2B SaaS & AI"]
    return []


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(1),
    reraise=True,
)
async def _send_targeted_turn(
    conversation_summary: str,
    current_message: str,
    captured_fields: dict[str, str],
    missing_fields: list[str],
    next_missing: str,
    is_ready_to_complete: bool,
) -> str:
    """Invokes Gemini 2.0 Flash with explicit instruction to ask ONE sharp follow-up question."""
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()

    if is_ready_to_complete:
        prompt = (
            f"You are PRISM's AI Intake Specialist. The founder has provided all key strategic parameters:\n"
            f"Summary: {json.dumps(captured_fields, indent=2)}\n\n"
            f"User says: {current_message}\n\n"
            f"DIRECTIVE:\n"
            f"In 2 enthusiastic sentences, confirm that all core parameters are locked in and that our 6-agent expert swarm "
            f"(VC, Lean Founder, Enterprise CTO, UX Researcher, Policy Regulator, Adversary) has been armed with their regional data.\n"
            f"Output INTAKE_COMPLETE on a new line at the very end."
        )
    else:
        prompt = (
            f"You are PRISM's AI Intake Specialist. You are having a natural, fast conversation with a startup founder.\n\n"
            f"CONVERSATION SO FAR:\n{conversation_summary}\n\n"
            f"CURRENT DOSSIER STATUS:\n"
            f"- Captured: {json.dumps(captured_fields, indent=2)}\n"
            f"- Still Missing: {missing_fields}\n"
            f"- Top Priority Missing Field to Ask Next: {next_missing}\n\n"
            f"Latest message from founder: {current_message}\n\n"
            f"STRICT RULES:\n"
            f"1. Keep your reply UNDER 3 SENTENCES TOTAL. Never write an essay, blueprint, or bulleted list.\n"
            f"2. Sentence 1: Warmly acknowledge what the founder just pitched.\n"
            f"3. Sentence 2: Ask EXACTLY ONE sharp, natural follow-up question specifically targeting: '{next_missing}'.\n"
            f"4. If asking about region/location, mention that it activates live regional regulations, currency rates, and market feeds.\n"
            f"5. Do NOT output INTAKE_COMPLETE until all fields are collected."
        )

    response = await asyncio.wait_for(
        asyncio.to_thread(
            model.generate_content,
            prompt,
            generation_config=GenerationConfig(
                temperature=0.3,
                max_output_tokens=256,
            ),
        ),
        timeout=12,
    )
    return response.text if hasattr(response, "text") else str(response)


async def run_conversation_turn(
    session_id: str,
    message: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Single conversation turn that extracts structured fields behind the scenes

    and dynamically asks follow-up questions for what is missing.
    Returns {"reply": str, "updated_history": list[dict], "is_complete": bool, "extraction": dict, ...}
    """
    if len(history) >= _MAX_TURNS:
        logger.warning("conversation_max_turns_reached", session_id=session_id)
        raise IntakeError("Maximum conversation length reached. Please submit your idea for processing.")

    clean_message = _sanitise_message(message)
    if not clean_message:
        raise IntakeError("Message cannot be empty")

    logger.info(
        "conversation_turn_start",
        session_id=session_id,
        turn=len(history),
    )

    # 1. Aggregate full user input across all turns
    past_user_texts = [t.get("content", "") for t in history if t.get("role") == "user"]
    all_user_text = " ".join(past_user_texts + [clean_message])

    conversation_summary = "\n".join(
        f"{t.get('role', 'user').capitalize()}: {t.get('content', '')}"
        for t in history[-4:]  # keep recent context
    )

    # 2. Extract structured fields from the conversation behind the scenes
    extraction = await extract_structured_fields(all_user_text)

    # 3. Analyze captured vs. missing parameters
    captured_fields: dict[str, str] = {}
    missing_fields: list[str] = []

    if extraction.raw_idea and len(extraction.raw_idea.strip()) >= 5:
        captured_fields["Core Idea"] = extraction.raw_idea[:160]
    else:
        missing_fields.append("business concept / what we are selling")

    if extraction.region:
        captured_fields["Target Region"] = extraction.region
    else:
        missing_fields.append("target region / launch country")

    if extraction.industry:
        captured_fields["Industry"] = extraction.industry
    else:
        missing_fields.append("industry vertical")

    if extraction.stage:
        captured_fields["Stage"] = extraction.stage
    else:
        missing_fields.append("development stage (new idea, prototype, team)")

    if extraction.budget_range:
        captured_fields["Budget / Income"] = extraction.budget_range
    else:
        missing_fields.append("budget or expected income range")

    if extraction.success_definition:
        captured_fields["12-Month Target"] = extraction.success_definition
    else:
        missing_fields.append("12-month success milestone")

    turn_count = len(history) // 2

    # Determine readiness: if 0 missing, or if >= 3 turns with region + industry + idea locked
    is_ready_to_complete = (
        len(missing_fields) == 0
        or (turn_count >= 3 and extraction.region and extraction.industry and len(missing_fields) <= 1)
    )

    # Pick single highest-priority missing field to ask next
    next_missing = "none"
    if not is_ready_to_complete and missing_fields:
        priority_order = [
            "target region / launch country",
            "development stage (new idea, prototype, team)",
            "budget or expected income range",
            "industry vertical",
            "12-month success milestone",
            "business concept / what we are selling",
        ]
        for priority in priority_order:
            if priority in missing_fields:
                next_missing = priority
                break
        if next_missing == "none":
            next_missing = missing_fields[0]

    # 4. Generate dynamic response via Gemini or resilient contextual fallback
    reply = ""
    try:
        reply = await _send_targeted_turn(
            conversation_summary=conversation_summary,
            current_message=clean_message,
            captured_fields=captured_fields,
            missing_fields=missing_fields,
            next_missing=next_missing,
            is_ready_to_complete=is_ready_to_complete,
        )
    except Exception as e:
        logger.warning("conversation_turn_targeted_fallback", session_id=session_id, error=str(e)[:120])
        if is_ready_to_complete:
            reg_display = captured_fields.get("Target Region", "your designated market")
            reply = (
                f"All core strategic parameters are locked in! We have your concept in {extraction.industry or 'tech'}, "
                f"target deployment in {reg_display}, {extraction.stage or 'initial'} stage, and operating goals. "
                f"All 6 expert agents are calibrated and standing by with live regional intelligence.\n\nINTAKE_COMPLETE"
            )
        elif "region" in next_missing or "country" in next_missing:
            reply = (
                "That's an exciting business concept! Where are you planning to set this up or launch first (e.g. India, US, UK, UAE)? "
                "Knowing your target region lets our 6 agents harvest live local regulations, currency volatility, and cultural demographics."
            )
        elif "stage" in next_missing:
            reply = (
                "Understood. Is this a brand-new idea starting fresh, or do you already have a working prototype or team in place?"
            )
        elif "budget" in next_missing or "income" in next_missing:
            reply = (
                "Got it. What approximate budget or revenue model are you projecting to operate with over the first 12 months?"
            )
        elif "success" in next_missing:
            reply = (
                "Makes sense! What primary milestone will define success for this venture in year one (e.g. active users, revenue, or enterprise pilots)?"
            )
        else:
            reply = (
                "Thank you! Could you share what type of business model or target customer segment this will focus on?"
            )

    is_complete = "INTAKE_COMPLETE" in reply or is_ready_to_complete
    clean_reply = reply.replace("INTAKE_COMPLETE", "").strip()

    updated_history = history + [
        {"role": "user", "content": clean_message},
        {"role": "model", "content": clean_reply},
    ]

    captured_count = 6 - len(missing_fields)
    completion_pct = int((captured_count / 6) * 100)
    suggested_chips = _get_suggested_chips(next_missing) if not is_complete else []

    logger.info(
        "conversation_turn_complete",
        session_id=session_id,
        turn=turn_count,
        is_complete=is_complete,
        captured_count=captured_count,
        completion_pct=completion_pct,
    )

    return {
        "reply": clean_reply,
        "updated_history": updated_history,
        "is_complete": is_complete,
        "extraction": extraction.model_dump(),
        "missing_fields": missing_fields,
        "captured_fields": captured_fields,
        "captured_count": captured_count,
        "completion_pct": completion_pct,
        "suggested_chips": suggested_chips,
    }
