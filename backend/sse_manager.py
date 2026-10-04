"""backend/sse_manager.py — Per-session SSE event queue manager."""

import asyncio
import json
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
    """
    Async generator consumed by the SSE route.
    Yields formatted SSE strings until _STREAM_DONE is received or timeout.
    """
    _TIMEOUT_SECONDS = 120   # max 2 minutes per stream
    try:
        while True:
            try:
                item = await asyncio.wait_for(
                    _queues[session_id].get(),
                    timeout=_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                logger.warning("sse_stream_timeout", session_id=session_id)
                yield f"event: timeout\ndata: {json.dumps({'event': 'timeout', 'session_id': session_id})}\n\n"
                break

            if item is _STREAM_DONE:
                yield f"event: done\ndata: {json.dumps({'event': 'done', 'session_id': session_id})}\n\n"
                break

            event_name = item.get("event", "message")
            raw_data = item.get("data", {})
            if isinstance(raw_data, dict):
                data_dict = {**raw_data, "event": event_name}
            else:
                data_dict = {"event": event_name, "data": raw_data}

            yield f"event: {event_name}\ndata: {json.dumps(data_dict)}\n\n"
    finally:
        cleanup_queue(session_id)
