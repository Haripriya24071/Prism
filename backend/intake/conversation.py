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

_INTAKE_SYSTEM_PROMPT = """You are PRISM's venture intake specialist and AI co-founder. Your job is to extract business parameters through a warm, concise conversation.

Rules:
- Ask exactly ONE follow-up question per turn. Never ask multiple questions or write long essays.
- Keep your reply under 3 sentences total.
- In 1 sentence, acknowledge what the founder shared (or state your autonomous recommendation if they are uncertain).
- In 1 sentence, ask ONE sharp follow-up question focusing on what is still missing.
- Once you have all 6 core parameters, output this exact token on its own line: INTAKE_COMPLETE
- When the user is uncertain or says they don't know, formulate an intelligent benchmark answer autonomously, lock it in, and advance."""

_UNCERTAINTY_KEYWORDS = (
    "don't know", "dont know", "do not know", "no idea", "not sure",
    "unsure", "uncertain", "haven't decided", "have not decided",
    "not decided", "yet to decide", "what do you recommend", "what do you suggest",
    "what should i", "what's best", "whats best", "you decide", "you choose",
    "help me decide", "help me choose", "recommend something", "suggest something",
    "not able to find out", "can't figure out", "cannot figure out", "hard to say",
    "confused", "no preference", "default", "suggest me", "you tell me",
    "not thought about", "havent thought", "whatever you think", "up to you",
    "no clue", "dunno", "idk",
)


def _detect_user_uncertainty(text: str) -> bool:
    """Detect if the user is expressing confusion, uncertainty, or asking the AI to decide."""
    lower = text.lower().strip()
    if any(kw in lower for kw in _UNCERTAINTY_KEYWORDS):
        return True
    if lower in {"maybe", "unsure", "any", "either", "not really", "?", "not certain"}:
        return True
    return False


def _determine_inquired_field(
    user_message: str,
    history: list[dict[str, Any]],
    current_missing: list[str],
) -> str:
    """Identify which field the user is uncertain about."""
    user_lower = user_message.lower()

    # 1. Check if the user explicitly named the parameter they don't know about
    if any(k in user_lower for k in ["budget", "income", "money", "runway", "cost", "funds", "funding", "dollars", "pricing"]):
        return "budget_range"
    if any(k in user_lower for k in ["region", "country", "market", "where", "location", "place", "geography"]):
        return "region"
    if any(k in user_lower for k in ["stage", "prototype", "mvp", "traction", "team"]):
        return "stage"
    if any(k in user_lower for k in ["milestone", "success", "year one", "target", "12-month", "arr", "revenue goal"]):
        return "success_definition"
    if any(k in user_lower for k in ["industry", "vertical", "sector"]):
        return "industry"

    # 2. Check the LAST question in the assistant's previous message
    last_assistant_msg = ""
    for msg in reversed(history):
        if msg.get("role") in ("model", "assistant"):
            last_assistant_msg = msg.get("content", "").lower()
            break

    sentences = [s.strip() for s in last_assistant_msg.split("?") if s.strip()]
    last_sentence = sentences[-1] if sentences else last_assistant_msg

    if any(k in last_sentence for k in ["budget", "income", "money", "runway", "operating with", "projecting"]):
        return "budget_range"
    if any(k in last_sentence for k in ["milestone", "success", "year one", "12-month", "define success"]):
        return "success_definition"
    if any(k in last_sentence for k in ["stage", "prototype", "fresh", "brand-new", "team in place"]):
        return "stage"
    if any(k in last_sentence for k in ["region", "country", "where are you planning", "where are we setting", "launch first", "geographic"]):
        return "region"
    if any(k in last_sentence for k in ["industry", "vertical", "business model", "customer segment"]):
        return "industry"

    for m in current_missing:
        if "budget" in m:
            return "budget_range"
        if "region" in m:
            return "region"
        if "stage" in m:
            return "stage"
        if "success" in m:
            return "success_definition"
        if "industry" in m:
            return "industry"

    return current_missing[0] if current_missing else "budget_range"


def _resolve_uncertain_field(
    target_field: str,
    raw_idea: str,
    industry: str | None,
) -> tuple[str, str, str]:
    """Generates an intelligent AI-recommended benchmark for an uncertain field.
    Returns (field_key, resolved_value, rationale).
    """
    idea_lower = raw_idea.lower()

    if target_field == "region":
        indian_cues = ["upi", "india", "rupee", "₹", "inr", "msme", "gst", "kirana", "tier-2", "bangalore", "mumbai", "delhi", "bharat"]
        uk_cues = ["uk", "united kingdom", "london", "fca", "nhs", "pound", "£"]
        uae_cues = ["uae", "dubai", "gulf", "aed", "dirham", "mena", "middle east"]

        if any(cue in idea_lower for cue in indian_cues):
            return "region", "IN", "India offers the highest real-time digital payment volume and an enormous 63M+ MSME customer base"
        elif any(cue in idea_lower for cue in uk_cues):
            return "region", "GB", "The UK provides clear Open Banking standards and mature regulatory sandboxes"
        elif any(cue in idea_lower for cue in uae_cues):
            return "region", "AE", "The UAE provides frictionless digital trade licensing and zero corporate tax freezones"
        else:
            return "region", "US", "The United States represents the largest commercial software market with highest willingness to pay"

    elif target_field == "stage":
        if any(w in idea_lower for w in ["prototype", "demo", "built a", "coded", "github", "mvp"]):
            return "stage", "prototype", "Calibrating as Working Prototype to stress-test your existing architecture"
        return "stage", "idea", "Benchmarking at Idea Stage to stress-test core unit economics before engineering spend"

    elif target_field == "budget_range":
        is_hardware = any(w in idea_lower for w in ["hardware", "device", "iot", "sensor", "drone", "manufacturing", "fleet", "factory"])
        if is_hardware:
            return "budget_range", "Seed Stage ($50k-$150k)", "Hardware and physical deployments require an initial prototyping runway of $50k–$150k"
        return "budget_range", "Bootstrapped / Pre-Seed ($10k-$25k)", "A lean $10,000–$25,000 budget allows building a working MVP to validate customer willingness-to-pay"

    elif target_field == "success_definition":
        is_b2b = any(w in idea_lower for w in ["b2b", "enterprise", "saas", "api", "compliance", "platform", "vendor", "firm", "truck", "fleet"])
        if is_b2b:
            return (
                "success_definition",
                "15 paying pilot customers and $30k ARR with positive unit economics",
                "Securing 15 committed pilot customers proves genuine market demand and willingness to pay",
            )
        return (
            "success_definition",
            "5,000 active users with >25% organic month-1 retention",
            "5,000 active users with strong organic retention is the gold standard benchmark for initial consumer traction",
        )

    elif target_field == "industry":
        if any(w in idea_lower for w in ["payment", "bank", "invoice", "fintech", "money", "loan", "lending", "credit"]):
            return "industry", "FinTech & Payments", "Mapped to FinTech & Financial Infrastructure"
        elif any(w in idea_lower for w in ["health", "medical", "doctor", "patient", "clinic"]):
            return "industry", "HealthTech & Digital Health", "Mapped to HealthTech"
        elif any(w in idea_lower for w in ["logistics", "freight", "truck", "delivery", "fleet", "transport"]):
            return "industry", "Logistics & Fleet Telematics", "Mapped to Logistics & Supply Chain"
        return "industry", "B2B SaaS & Automation", "Mapped to B2B SaaS & Applied AI"

    return target_field, "AI Benchmark Applied", "Standard venture baseline"


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
    uncertainty_resolution: dict[str, str] | None = None,
) -> str:
    """Invokes Gemini 2.0 Flash with explicit instruction to ask ONE sharp follow-up question."""
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()

    if is_ready_to_complete:
        prompt = (
            f"You are PRISM's AI Intake Specialist. The founder has confirmed all key strategic parameters:\n"
            f"Summary: {json.dumps(captured_fields, indent=2)}\n\n"
            f"User says: {current_message}\n\n"
            f"DIRECTIVE:\n"
            f"In 2 enthusiastic sentences, confirm that all core parameters are locked in and that our 6-agent expert swarm "
            f"(VC, Lean Founder, Enterprise CTO, UX Researcher, Policy Regulator, Adversary) has been armed with their regional data.\n"
            f"Output INTAKE_COMPLETE on a new line at the very end."
        )
    elif uncertainty_resolution:
        param_label = uncertainty_resolution.get("field_label", "parameter")
        recommended_val = uncertainty_resolution.get("value", "")
        rationale = uncertainty_resolution.get("rationale", "")
        prompt = (
            f"You are PRISM's AI Intake Specialist acting as a warm, reassuring venture co-founder.\n"
            f"The founder expressed uncertainty or said they don't know: '{current_message}'.\n"
            f"You analyzed their venture context and autonomously decided on the optimal industry-standard benchmark:\n"
            f"- Parameter: {param_label}\n"
            f"- AI Benchmark Chosen: {recommended_val}\n"
            f"- Rationale: {rationale}\n\n"
            f"CONVERSATION SO FAR:\n{conversation_summary}\n\n"
            f"CURRENT DOSSIER STATUS:\n"
            f"- Captured: {json.dumps(captured_fields, indent=2)}\n"
            f"- Still Missing: {missing_fields}\n"
            f"- Next Parameter to Ask: {next_missing}\n\n"
            f"STRICT RULES:\n"
            f"1. Keep your reply UNDER 3 SENTENCES TOTAL.\n"
            f"2. Sentence 1: Reassure the founder that uncertainty here is completely normal, and state that you've benchmarked {param_label} as '{recommended_val}' ({rationale}).\n"
            f"3. Sentence 2: In ONE focused question, ask the next missing parameter: '{next_missing}'. (If all 6 fields are now resolved, announce that all parameters are locked and output INTAKE_COMPLETE on a new line).\n"
            f"4. Never make the founder feel bad for not knowing. Be encouraging and proactive.\n"
            f"5. Do NOT output INTAKE_COMPLETE until all fields are collected."
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
    prior_extraction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Single conversation turn that extracts structured fields behind the scenes,
    dynamically asks follow-up questions for what is missing, and autonomously decides
    benchmarks when the user expresses uncertainty or says 'I don't know'.
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

    # 3. Preserve prior extracted or recommended fields
    if prior_extraction and isinstance(prior_extraction, dict):
        if not extraction.raw_idea and prior_extraction.get("raw_idea"):
            extraction.raw_idea = str(prior_extraction["raw_idea"])
        if not extraction.region and prior_extraction.get("region"):
            extraction.region = str(prior_extraction["region"])
        if not extraction.industry and prior_extraction.get("industry"):
            extraction.industry = str(prior_extraction["industry"])
        if not extraction.stage and prior_extraction.get("stage"):
            extraction.stage = prior_extraction["stage"]
        if not extraction.budget_range and prior_extraction.get("budget_range"):
            extraction.budget_range = str(prior_extraction["budget_range"])
        if not extraction.success_definition and prior_extraction.get("success_definition"):
            extraction.success_definition = str(prior_extraction["success_definition"])

    # 4. Detect user uncertainty and autonomously decide the parameter
    uncertainty_resolution: dict[str, str] | None = None
    is_uncertain = _detect_user_uncertainty(clean_message)

    if is_uncertain:
        # Determine which parameter the user is uncertain about
        target_param = _determine_inquired_field(clean_message, history, [
            f for f, v in [
                ("budget_range", extraction.budget_range),
                ("region", extraction.region),
                ("stage", extraction.stage),
                ("success_definition", extraction.success_definition),
                ("industry", extraction.industry),
            ] if not v
        ])

        # If that parameter was already resolved, fallback to the next truly missing field
        if getattr(extraction, target_param, None) is not None:
            for cand in ["budget_range", "region", "stage", "success_definition", "industry"]:
                if getattr(extraction, cand, None) is None:
                    target_param = cand
                    break

        # Formulate and lock the AI benchmark
        if getattr(extraction, target_param, None) is None:
            field_key, resolved_val, rationale = _resolve_uncertain_field(
                target_param,
                extraction.raw_idea or clean_message,
                extraction.industry,
            )
            setattr(extraction, field_key, resolved_val)

            label_map = {
                "region": "Target Launch Region",
                "stage": "Development Stage",
                "budget_range": "Starting Budget & Runway",
                "success_definition": "12-Month Success Target",
                "industry": "Industry Sector",
            }
            uncertainty_resolution = {
                "field_key": field_key,
                "field_label": label_map.get(field_key, field_key),
                "value": resolved_val,
                "rationale": rationale,
            }
            logger.info(
                "ai_autonomous_decision_applied",
                session_id=session_id,
                field=field_key,
                value=resolved_val,
                rationale=rationale,
            )

    # 5. Analyze captured vs. missing parameters
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

    # 6. Generate dynamic response via Gemini or resilient contextual fallback
    reply = ""
    try:
        reply = await _send_targeted_turn(
            conversation_summary=conversation_summary,
            current_message=clean_message,
            captured_fields=captured_fields,
            missing_fields=missing_fields,
            next_missing=next_missing,
            is_ready_to_complete=is_ready_to_complete,
            uncertainty_resolution=uncertainty_resolution,
        )
    except Exception as e:
        logger.warning("conversation_turn_targeted_fallback", session_id=session_id, error=str(e)[:120])
        if uncertainty_resolution:
            param_label = uncertainty_resolution.get("field_label", "parameter")
            val = uncertainty_resolution.get("value", "")
            rationale = uncertainty_resolution.get("rationale", "")
            if is_ready_to_complete:
                reply = (
                    f"No worries at all! Based on your concept, I've benchmarked your {param_label} as **{val}** ({rationale}). "
                    f"With that, all 6 core parameters are locked in! All 6 expert agents are standing by to run their evaluations.\n\nINTAKE_COMPLETE"
                )
            elif "region" in next_missing or "country" in next_missing:
                reply = (
                    f"No problem! Based on venture benchmarks, I've locked your {param_label} as **{val}** ({rationale}).\n\n"
                    f"Where are you planning to set this up or launch first (e.g. India, US, UK, UAE)? "
                    f"This activates live local regulations, currency rates, and geopolitical risk feeds."
                )
            elif "stage" in next_missing:
                reply = (
                    f"No problem! Based on standard venture benchmarks, I've locked your {param_label} as **{val}** ({rationale}).\n\n"
                    f"Is this a brand-new idea starting fresh, or do you already have a working prototype or team in place?"
                )
            elif "budget" in next_missing or "income" in next_missing:
                reply = (
                    f"Understood! Based on standard early-stage benchmarks, I've locked your {param_label} as **{val}** ({rationale}).\n\n"
                    f"What approximate budget or revenue model are you projecting to operate with over the first 12 months?"
                )
            elif "success" in next_missing:
                reply = (
                    f"Makes total sense! I've set your {param_label} to **{val}** ({rationale}) in your blueprint.\n\n"
                    f"What primary milestone will define success for this venture in year one (e.g. active users, revenue, or enterprise pilots)?"
                )
            else:
                reply = (
                    f"Got it! I've set your {param_label} to **{val}** ({rationale}) in your blueprint.\n\n"
                    f"Could you share what type of business model or target customer segment this will focus on?"
                )
        elif is_ready_to_complete:
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
