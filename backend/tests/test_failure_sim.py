"""backend/tests/test_failure_sim.py — Unit tests for failure simulation module."""

import pytest
from backend.models.agents import AgentOutput, AgentPersona
from backend.output.failure_sim import extract_failure_modes


@pytest.mark.asyncio
async def test_extract_failure_modes_from_agent_output():
    agent_output = AgentOutput(
        agent=AgentPersona.ADVERSARIAL,
        raw_text="The startup risks severe margin compression due to high acquisition costs and heavy regulatory fines.",
        brd_json={"critical_risks": ["Unit economics failure", "Regulatory compliance fine"]},
    )
    modes = await extract_failure_modes(agent_output)
    assert isinstance(modes, list)
    assert len(modes) > 0
    assert hasattr(modes[0], "title")
    assert hasattr(modes[0], "probability_pct")
    assert hasattr(modes[0], "mitigation")
    assert 0 <= modes[0].probability_pct <= 100


@pytest.mark.asyncio
async def test_extract_failure_modes_empty_fallback():
    modes = await extract_failure_modes(None)
    assert isinstance(modes, list)
    assert len(modes) == 3
    assert "Unit Economics" in modes[0].title
