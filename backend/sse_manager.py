"""backend/sse_manager.py — Per-session SSE event queue manager."""

import asyncio
from collections import defaultdict
from typing import Any, Dict, AsyncGenerator
import structlog

logger = structlog.get_logger()

# Per-session event queues — pipeline puts, SSE route gets
_queues: Dict[str, asyncio.Queue[Any]] = defaultdict(lambda: asyncio.Queue(maxsize=50))

# Sentinel to signal stream end
_STREAM_DONE: Any = object()


def get_queue(session_id: str) -> asyncio.Queue[Any]:
    """Get or create the asyncio.Queue for a given session ID."""
    return _queues[session_id]


def cleanup_queue(session_id: str) -> None:
    """Remove session event queue from memory."""
    if session_id in _queues:
        del _queues[session_id]
        logger.debug("sse_queue_cleaned", session_id=session_id)


async def publish(session_id: str, event: str, data: Dict[str, Any], progress_pct: int = 0) -> None:
    """
    Put one SSE event onto the session queue.
    Called by the pipeline — non-blocking (queue has maxsize=50).
    """
    payload = {
        "event": event,
        "data": {
            "session_id": session_id,
            "status": data.get("status", event),
            "progress_pct": progress_pct,
            **{k: v for k, v in data.items() if k != "status"},
        },
    }
    try:
        _queues[session_id].put_nowait(payload)
    except asyncio.QueueFull:
        logger.warning("sse_queue_full", session_id=session_id, event=event)


async def publish_done(session_id: str) -> None:
    """Signal that the stream is complete. SSE route will close the connection."""
    try:
        _queues[session_id].put_nowait(_STREAM_DONE)
    except asyncio.QueueFull:
        pass


async def event_generator(session_id: str) -> AsyncGenerator[str, None]:
    raise NotImplementedError("Stub for Commit 2")
    yield ""
