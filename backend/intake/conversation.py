"""backend/intake/conversation.py — Conversational intake turn handler."""

from typing import Any, TYPE_CHECKING
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

if TYPE_CHECKING:
    from backend.errors import IntakeError
    from backend.config import get_flash_model
else:
    try:
        from backend.errors import IntakeError
        from backend.config import get_flash_model
    except ImportError:
        from errors import IntakeError
        from config import get_flash_model

logger = structlog.get_logger()

_MAX_TURNS = 10
_MAX_MSG_LEN = 2000

_INTAKE_SYSTEM_PROMPT = """You are PRISM's intake specialist. Your only job is to extract a business idea through natural conversation.

Rules you must follow:
- Ask exactly ONE follow-up question per turn. Never ask two questions at once.
- Be concise and warm. This is a conversation, not a form.
- You are trying to extract these six fields:
    1. region       — what country or region will this launch in?
    2. industry     — what industry or sector does this belong to?
    3. stage        — is this an idea, prototype, MVP, or growth-stage product?
    4. budget_range — what is the approximate budget available?
    5. success_definition — how will the founder know this succeeded in 12 months?
    6. raw_idea     — the core idea in the founder's own words

- Once you have confident answers for all six, output this exact token on its own line: INTAKE_COMPLETE
- Do not output INTAKE_COMPLETE until you have all six fields.
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


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def _send_turn(history_contents: list[Any], message: str) -> str:
    """Inner retried call. Returns model reply text."""
    from vertexai.generative_models import GenerationConfig

    model = get_flash_model()
    chat = model.start_chat(history=history_contents)  # type: ignore[attr-defined]
    response = chat.send_message(
        message,
        generation_config=GenerationConfig(
            temperature=0.4,
            max_output_tokens=512,
        ),
    )
    return response.text  # type: ignore[no-any-return]


async def run_conversation_turn(
    session_id: str,
    message: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Single conversation turn with Gemini 2.0 Flash via Vertex AI.

    Returns {"reply": str, "updated_history": list[dict], "is_complete": bool}
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
        # never log message content — PII
    )

    history_contents = _build_history(history)

    try:
        reply = await _send_turn(history_contents, clean_message)
    except Exception as e:
        logger.error("conversation_turn_failed", session_id=session_id, error_type=type(e).__name__)
        raise IntakeError("Conversation failed. Please try again.", detail=str(e))

    is_complete = "INTAKE_COMPLETE" in reply
    clean_reply = reply.replace("INTAKE_COMPLETE", "").strip()

    updated_history = history + [
        {"role": "user", "content": clean_message},
        {"role": "model", "content": clean_reply},
    ]

    logger.info(
        "conversation_turn_complete",
        session_id=session_id,
        turn=len(history),
        is_complete=is_complete,
        # never log reply content
    )

    return {
        "reply": clean_reply,
        "updated_history": updated_history,
        "is_complete": is_complete,
    }
