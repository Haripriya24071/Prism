from dataclasses import dataclass
from models.intake import IntakeExtraction


@dataclass
class DemoScenario:
    name: str
    session_id_prefix: str
    extraction: IntakeExtraction
    expected_score_range: tuple[int, int]   # (min, max) — for validation
    demo_talking_points: list[str]


DEMO_SCENARIOS: list[DemoScenario] = [
    DemoScenario(
        name="IndiaFintechSMB",
        session_id_prefix="demo-fintech",
        extraction=IntakeExtraction(
            raw_idea="A mobile app for Indian SMBs to manage GST invoices, track payments, and access working capital loans from partner NBFCs. Targets kirana stores and small manufacturers in tier-2 cities.",
            region="IN",
            industry="fintech",
            stage="idea",
            budget_range="50000 USD",
            success_definition="1000 paying SMBs generating INR 5L MRR within 12 months",
        ),
        expected_score_range=(55, 85),
        demo_talking_points=[
            "Watch the REGULATOR agent flag DPDP Act and RBI licensing immediately",
            "ADVERSARIAL agent will cite Razorpay and Khatabook as kill shots",
            "World Bank GDP data for India grounds the market size claim",
            "Pivot suggester may fire if score < 60 — shows tier-2 niche pivot",
        ],
    ),
    DemoScenario(
        name="SingaporeEdTechB2B",
        session_id_prefix="demo-edtech",
        extraction=IntakeExtraction(
            raw_idea="An AI-powered corporate learning platform for Singapore enterprises. Employees complete micro-learning modules in 5 minutes per day. HR managers get real-time skill gap analytics and compliance training tracking.",
            region="SG",
            industry="edtech",
            stage="mvp",
            budget_range="200000 USD",
            success_definition="10 enterprise clients with 500+ seats each within 18 months",
        ),
        expected_score_range=(60, 90),
        demo_talking_points=[
            "MAS and IMDA regulatory context surfaces from govtdata",
            "VC agent will highlight Singapore as APAC launch hub with regional expansion story",
            "CTO agent will focus on PDPA data residency for HR data",
            "Score likely above 60 so pivot suggester stays silent — show this as intentional",
        ],
    ),
    DemoScenario(
        name="USHealthTechConsumer",
        session_id_prefix="demo-healthtech",
        extraction=IntakeExtraction(
            raw_idea="A mental health app for US college students. AI-powered daily mood check-ins, CBT-based exercises, and anonymous peer support groups. Partners with university counselling centres for referrals.",
            region="US",
            industry="healthtech",
            stage="prototype",
            budget_range="150000 USD",
            success_definition="50000 active users across 20 universities within 12 months",
        ),
        expected_score_range=(50, 80),
        demo_talking_points=[
            "REGULATOR agent will flag HIPAA, FERPA, and FDA SaMD classification immediately",
            "UX agent will surface mental health UX ethics — no dark patterns, crisis protocols",
            "ADVERSARIAL will cite Headspace and BetterHelp as well-funded rivals",
            "Assumption flagging will catch 'university partnerships' as unvalidated",
        ],
    ),
]

# NewsAPI pre-warm pairs — one per demo scenario
# Call prewarm_cache() with this list before the demo starts
PREWARM_PAIRS: list[tuple[str, str]] = [
    ("IN", "fintech"),
    ("SG", "edtech"),
    ("US", "healthtech"),
]

# Quick lookup by name
SCENARIOS_BY_NAME: dict[str, DemoScenario] = {s.name: s for s in DEMO_SCENARIOS}
