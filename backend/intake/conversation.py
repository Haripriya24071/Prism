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


async def run_conversation_turn(
    session_id: str,
    message: str,
    history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Single Gemini 2.0 Flash turn via Vertex AI. Returns {reply: str, updated_history: list}."""
    raise NotImplementedError("Phase 4")
