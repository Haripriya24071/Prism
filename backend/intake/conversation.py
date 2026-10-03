"""backend/intake/conversation.py — Conversational intake turn handler."""


async def run_conversation_turn(
    session_id: str,
    message: str,
    history: list[dict],
) -> dict:
    """Single Gemini 2.0 Flash turn via Vertex AI. Returns {reply: str, updated_history: list}."""
    raise NotImplementedError("Phase 4")
