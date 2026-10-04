"""backend/tests/test_assumptions.py — Unit tests for assumptions flagging module."""

import pytest
from backend.models.brd import BRDSection, LineageTag, MergedBRD
from backend.models.agents import AgentPersona
from backend.models.context import ContextPackage, MarketData
from backend.output.assumptions import flag_assumptions


@pytest.fixture
def sample_merged_brd():
    return MergedBRD(
        session_id="12345678-1234-5678-1234-567812345678",
        sections=[
            BRDSection(
                title="Market Opportunity",
                content="We assume customer acquisition cost will remain low through referral viral loops.",
                lineage=LineageTag(source_agent=AgentPersona.VC, confidence=0.85, data_citation="Industry Benchmarks"),
            ),
            BRDSection(
                title="Technical Architecture",
                content="System is expected to handle 10k concurrent users using serverless containers.",
                lineage=LineageTag(source_agent=AgentPersona.ENTERPRISE_CTO, confidence=0.90, data_citation="Cloud Specs"),
            ),
        ],
        investor_readiness_score=85,
    )


@pytest.fixture
def sample_context():
    return ContextPackage(
        session_id="12345678-1234-5678-1234-567812345678",
        region="IN",
        industry="Fintech",
        market_data=MarketData(inflation_rate_pct=5.5, gdp_per_capita_usd=2500.0),
        regulatory_flags=["RBI DPDP Act"],
    )


@pytest.mark.asyncio
async def test_flag_assumptions_returns_list(sample_merged_brd, sample_context):
    flags = await flag_assumptions(sample_merged_brd, sample_context)
    assert isinstance(flags, list)
    assert len(flags) > 0
    assert hasattr(flags[0], "assumption")
    assert hasattr(flags[0], "confidence")
    assert hasattr(flags[0], "recommended_action")


@pytest.mark.asyncio
async def test_flag_assumptions_invalid_input():
    flags = await flag_assumptions(None, None)
    assert isinstance(flags, list)
    assert len(flags) > 0
