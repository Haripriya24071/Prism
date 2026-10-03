"""backend/session_store.py — In-memory session CRUD and TTL cleanup background task."""

import asyncio
from datetime import datetime, timedelta
from typing import Any
import uuid

import structlog

from backend.config import settings

logger = structlog.get_logger()

# In-memory storage for hackathon session persistence
_sessions: dict[str, dict[str, Any]] = {}


def create_session() -> str:
    """Create a new session with default state and UUID4 identifier."""
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    session_data: dict[str, Any] = {
        "session_id": session_id,
        "created_at": now,
        "last_accessed": now,
        "status": "intake",
        "conversation_history": [],
        "intake_package": None,
        "context_package": None,
        "brd": None,
        "score": None,
        "pitch_deck": None,
        "error": None,
    }
    _sessions[session_id] = session_data
    logger.info("session_created", session_id=session_id)
    return session_id


def get_session(session_id: str) -> dict[str, Any] | None:
    """Retrieve session by ID, returning None if missing or expired."""
    session = _sessions.get(session_id)
    if session is None:
        return None

    now = datetime.utcnow()
    ttl = timedelta(seconds=settings.SESSION_TTL_SECONDS)
    if now - session["last_accessed"] > ttl:
        _sessions.pop(session_id, None)
        logger.info("session_expired", session_id=session_id)
        return None

    session["last_accessed"] = now
    return session


def update_session(session_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    """Update fields of an existing active session."""
    session = get_session(session_id)
    if session is None:
        return None

    session.update(updates)
    session["last_accessed"] = datetime.utcnow()
    logger.info("session_updated", session_id=session_id, updated_keys=list(updates.keys()))
    return session


def set_session_status(session_id: str, status: str, error: str | None = None) -> dict[str, Any] | None:
    """Set the status and optional error for a session."""
    updates: dict[str, Any] = {"status": status}
    if error is not None:
        updates["error"] = error
    return update_session(session_id, updates)


async def cleanup_expired_sessions(interval_seconds: int = 300) -> None:
    """Background task to periodically purge expired sessions from memory."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            now = datetime.utcnow()
            ttl = timedelta(seconds=settings.SESSION_TTL_SECONDS)
            expired_ids = [
                sid for sid, s in list(_sessions.items())
                if now - s["last_accessed"] > ttl
            ]
            for sid in expired_ids:
                _sessions.pop(sid, None)
                logger.info("session_cleaned_up", session_id=sid)
        except Exception as e:
            logger.error("session_cleanup_error", error=str(e))
