import pytest
import json
from backend.sse_manager import publish, publish_done, event_generator, get_queue, cleanup_queue

@pytest.mark.asyncio
async def test_sse_event_generator_yields_proper_sse_format():
    session_id = "test-session-sse-123"
    cleanup_queue(session_id)
    
    await publish(session_id, "agent_status", {"agent": "vc", "status": "complete"}, progress_pct=40)
    await publish_done(session_id)
    
    gen = event_generator(session_id)
    first_item = await anext(gen)
    assert first_item.startswith("event: agent_status\n")
    assert "data: " in first_item
    assert first_item.endswith("\n\n")
    
    # Verify JSON content
    data_line = [l for l in first_item.split("\n") if l.startswith("data: ")][0]
    payload = json.loads(data_line[6:])
    assert payload["event"] == "agent_status"
    assert payload["agent"] == "vc"
    assert payload["status"] == "complete"
    assert payload["progress_pct"] == 40
    
    # Verify done event
    done_item = await anext(gen)
    assert done_item.startswith("event: done\n")
    assert "data: " in done_item
    
    cleanup_queue(session_id)
