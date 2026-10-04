"""backend/tests/test_pdf_export.py — Unit tests for PDF export module."""

import pytest
from backend.models.agents import AgentPersona
from backend.models.brd import AssumptionFlag, BRDSection, FailureMode, LineageTag, MergedBRD
from backend.output.pdf_export import generate_pdf


@pytest.fixture
def complete_merged_brd():
    return MergedBRD(
        session_id="12345678-1234-5678-1234-567812345678",
        sections=[
            BRDSection(
                title="Market Analysis",
                content="Growing 25% YoY with 50M addressable SMBs across India.",
                lineage=LineageTag(source_agent=AgentPersona.VC, confidence=0.88, data_citation="World Bank 2024"),
            ),
            BRDSection(
                title="System Architecture",
                content="Event-driven architecture with FastAPI and GCS storage.",
                lineage=LineageTag(source_agent=AgentPersona.ENTERPRISE_CTO, confidence=0.92, data_citation="Tech PRD"),
            ),
            BRDSection(
                title="Regulatory Compliance",
                content="Complies with DPDP Act 2023 and RBI lending norms.",
                lineage=LineageTag(source_agent=AgentPersona.REGULATOR, confidence=0.95, data_citation="RBI Handbook"),
            ),
        ],
        assumptions=[
            AssumptionFlag(
                assumption="Low user churn",
                confidence="medium",
                evidence="Cohort retention",
                recommended_action="Run A/B onboarding test",
            )
        ],
        failure_modes=[
            FailureMode(
                title="API Quota Exhaustion",
                probability_pct=25,
                description="Harvester runs out of daily requests.",
                mitigation="Cache responses with TTL.",
            )
        ],
        investor_readiness_score=88,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("view", ["investor", "technical", "regulatory"])
async def test_generate_pdf_views(complete_merged_brd, view):
    pdf_bytes = await generate_pdf(complete_merged_brd, view)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
