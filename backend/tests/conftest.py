import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Generator
import pytest

# Ensure backend directory is in sys.path for direct imports
_BACKEND_DIR = Path(__file__).parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from models.agents import AgentOutput, AgentPersona, ScoreMatrix, SectionScore
from models.brd import BRDSection, LineageTag, MergedBRD
from models.context import ContextPackage, MarketData, NewsItem
from models.intake import IntakeExtraction, IntakePackage




# ── Intake fixtures ───────────────────────────────────────────────────

@pytest.fixture
def sample_extraction() -> IntakeExtraction:
    return IntakeExtraction(
        raw_idea="A fintech app for SMBs in India to manage invoices and payments",
        region="IN",
        industry="fintech",
        stage="idea",
        budget_range="50000 USD",
        success_definition="1000 paying customers in 12 months",
    )

@pytest.fixture
def sample_intake(sample_extraction: IntakeExtraction) -> IntakePackage:
    return IntakePackage(
        session_id="test-session-fixture-01",
        extraction=sample_extraction,
        conversation_history=[
            {"role": "user",  "content": "I want to build a fintech app"},
            {"role": "model", "content": "What region will you launch in?"},
            {"role": "user",  "content": "India"},
        ],
        created_at=datetime.utcnow(),
    )

# ── Context fixtures ──────────────────────────────────────────────────

@pytest.fixture
def sample_context() -> ContextPackage:
    return ContextPackage(
        session_id="test-session-fixture-01",
        region="IN",
        industry="fintech",
        news_items=[
            NewsItem(title="Fintech Booms in India", source="TechCrunch", url="https://example.com/1", published_at="2024-01-01"),
            NewsItem(title="RBI Opens Sandbox", source="Economic Times", url="https://example.com/2"),
        ],
        market_data=MarketData(
            gdp_per_capita_usd=2389.0,
            ease_of_doing_business_rank=63,
            inflation_rate_pct=5.7,
            source_year=2023,
        ),
        crunchbase_data={
            "recent_rounds": [{"company": "Razorpay", "amount_usd": 5_000_000, "round": "Seed"}],
            "data_source": "static_fallback",
        },
        regulatory_flags=["DPDP Act 2023 applies", "RBI licensing required", "PCI-DSS for card data"],
        cultural_context="India has strong UPI adoption. Mobile-first approach critical.",
        failed_sources=[],
    )

# ── Agent output fixtures ─────────────────────────────────────────────

@pytest.fixture
def sample_agent_output_vc() -> AgentOutput:
    return AgentOutput(
        agent=AgentPersona.VC,
        brd_json={
            "Executive Summary": "Strong TAM of $50B [SOURCE: worldbank]. Mobile penetration at 85% [SOURCE: grounding].",
            "Market Analysis": "Fintech sector raised $7M recently [SOURCE: crunchbase].",
            "Functional Requirements": "Invoice management, payment gateway, GST filing [SOURCE: founder].",
            "Technical Requirements": "React Native app, FastAPI backend, Supabase [SOURCE: founder].",
            "Risk Register": '[{"title":"Regulatory Block","probability_pct":65,"description":"RBI may restrict.","mitigation":"Apply for sandbox early."}]',
            "Go-To-Market Strategy": "Target CA firms first. Partner with tally [SOURCE: founder].",
        },
        raw_text="raw vc response",
        completed_at=datetime.utcnow(),
        duration_ms=8200,
        failed=False,
    )

@pytest.fixture
def sample_agent_output_adversarial() -> AgentOutput:
    return AgentOutput(
        agent=AgentPersona.ADVERSARIAL,
        brd_json={
            "Executive Summary": "This product will fail [SOURCE: founder].",
            "Market Analysis": "Razorpay already dominates [SOURCE: crunchbase].",
            "Functional Requirements": "Features are not differentiated [SOURCE: founder].",
            "Technical Requirements": "No moat in the tech stack [SOURCE: founder].",
            "Risk Register": '[{"title":"Incumbent Dominance","probability_pct":80,"description":"Razorpay/Stripe will copy.","mitigation":"Niche down to tier-2 cities."},{"title":"Regulatory Risk","probability_pct":60,"description":"RBI rules are changing.","mitigation":"Get legal counsel."},{"title":"Funding Drought","probability_pct":55,"description":"Seed market is tight.","mitigation":"Bootstrap to $10K MRR first."}]',
            "Go-To-Market Strategy": "No differentiated GTM [SOURCE: founder].",
        },
        raw_text="raw adversarial response",
        completed_at=datetime.utcnow(),
        duration_ms=7800,
        failed=False,
    )

@pytest.fixture
def all_agent_outputs(sample_agent_output_vc: AgentOutput, sample_agent_output_adversarial: AgentOutput) -> list[AgentOutput]:
    """6 outputs — VC and ADVERSARIAL are real, others are minimal passing stubs."""
    stubs = []
    for persona in [AgentPersona.LEAN_FOUNDER, AgentPersona.ENTERPRISE_CTO, AgentPersona.UX_RESEARCHER, AgentPersona.REGULATOR]:
        stubs.append(AgentOutput(
            agent=persona,
            brd_json={
                "Executive Summary": f"{persona.value} exec summary [SOURCE: founder].",
                "Market Analysis": f"{persona.value} market [SOURCE: worldbank].",
                "Functional Requirements": f"{persona.value} features [SOURCE: founder].",
                "Technical Requirements": f"{persona.value} tech [SOURCE: founder].",
                "Risk Register": f"{persona.value} risks [SOURCE: govtdata].",
                "Go-To-Market Strategy": f"{persona.value} GTM [SOURCE: founder].",
            },
            raw_text=f"raw {persona.value} response",
            completed_at=datetime.utcnow(),
            duration_ms=7500,
            failed=False,
        ))
    return [sample_agent_output_vc] + stubs + [sample_agent_output_adversarial]

# ── Score matrix fixture ──────────────────────────────────────────────

@pytest.fixture
def sample_score_matrix() -> ScoreMatrix:
    scores = {}
    base_vals = {
        AgentPersona.VC:              (85, 80, 70, 75, 78),
        AgentPersona.LEAN_FOUNDER:    (70, 65, 68, 72, 60),
        AgentPersona.ENTERPRISE_CTO:  (75, 70, 85, 80, 72),
        AgentPersona.UX_RESEARCHER:   (72, 68, 65, 88, 65),
        AgentPersona.REGULATOR:       (68, 65, 90, 70, 60),
        AgentPersona.ADVERSARIAL:     (45, 50, 55, 48, 40),
    }
    for persona, (f, mt, rs, ua, cm) in base_vals.items():
        composite = round(f*0.25 + mt*0.20 + rs*0.20 + ua*0.20 + cm*0.15, 2)
        scores[persona.value] = SectionScore(
            feasibility=f, market_timing=mt, regulatory_safety=rs,
            user_adoption=ua, competitive_moat=cm,
            composite=composite, data_citation="test fixture",
        )
    return ScoreMatrix(
        session_id="test-session-fixture-01",
        scores=scores,
        winning_agent=AgentPersona.VC,
    )

# ── Merged BRD fixture ────────────────────────────────────────────────

@pytest.fixture
def sample_merged_brd() -> MergedBRD:
    sections = []
    section_defs = [
        ("Executive Summary",      AgentPersona.VC,           0.88),
        ("Market Analysis",        AgentPersona.ENTERPRISE_CTO, 0.82),
        ("Functional Requirements",AgentPersona.UX_RESEARCHER, 0.79),
        ("Technical Requirements", AgentPersona.ENTERPRISE_CTO, 0.85),
        ("Risk Register",          AgentPersona.REGULATOR,    0.91),
        ("Go-To-Market Strategy",  AgentPersona.VC,           0.84),
    ]
    for title, agent, confidence in section_defs:
        sections.append(BRDSection(
            title=title,
            content=f"This is the {title} section with real content [SOURCE: worldbank] and more detail [SOURCE: newsapi].",
            lineage=LineageTag(source_agent=agent, confidence=confidence, data_citation="fixture data"),
        ))
    return MergedBRD(
        session_id="test-session-fixture-01",
        sections=sections,
        assumptions=[],
        failure_modes=[],
        investor_readiness_score=None,
    )

# ── FastAPI test client ───────────────────────────────────────────────

@pytest.fixture
def test_client() -> Generator:
    import os
    os.environ["GCP_PROJECT_ID"] = "test-project"
    os.environ["ENV"] = "development"
    from fastapi.testclient import TestClient
    try:
        from backend.main import app
    except ImportError:
        from main import app
    with TestClient(app) as client:
        yield client
