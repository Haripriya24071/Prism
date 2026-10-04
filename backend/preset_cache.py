"""backend/preset_cache.py — Persistent cache for demo presets and repeated idea runs."""

import hashlib
import json
from pathlib import Path
from typing import Any
import structlog

logger = structlog.get_logger()

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache" / "presets"
FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

KNOWN_PRESETS = {
    "b2b_code_review": ["code review", "vulnerability", "github pull request", "b2b ai code review"],
    "p2p_social_lending": ["micro-lending", "p2p", "consumer micro-lending", "social lending"],
    "rural_telehealth": ["telehealth", "rural health", "triage", "disha"],
    "global_paytech": ["paytech", "fincen", "cross-border", "mica"],
}


def get_preset_key(text: str) -> str:
    """Returns a deterministic preset slug or a content-based SHA256 hash."""
    if not text:
        return "default"

    lower = text.lower().strip()
    if lower.endswith(".json"):
        lower = lower[:-5]

    # Direct match on known preset names
    if lower in KNOWN_PRESETS:
        return lower

    # Check if a cache file directly exists with this name
    if (CACHE_DIR / f"{lower}.json").exists():
        return lower

    for preset_name, keywords in KNOWN_PRESETS.items():
        if preset_name in lower or lower in preset_name:
            return preset_name
        if any(kw in lower for kw in keywords):
            return preset_name

    # Normalized content hash for arbitrary pitches
    clean = " ".join(lower.split())
    return "idea_" + hashlib.sha256(clean.encode("utf-8")).hexdigest()[:16]


def _ensure_preseeded_fixtures() -> None:
    """Ensure all 4 demonstration preset fixtures are seeded in data/cache/presets/."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. B2B Code Review
    b2b_file = CACHE_DIR / "b2b_code_review.json"
    if not b2b_file.exists() and (FIXTURES_DIR / "merged_brd.json").exists():
        try:
            with open(FIXTURES_DIR / "merged_brd.json", "r", encoding="utf-8") as f:
                brd = json.load(f)
            with open(FIXTURES_DIR / "investor_readiness.json", "r", encoding="utf-8") as f:
                inv = json.load(f)
            with open(FIXTURES_DIR / "heatmap.json", "r", encoding="utf-8") as f:
                hm = json.load(f)
            with open(FIXTURES_DIR / "score_matrix.json", "r", encoding="utf-8") as f:
                sm = json.load(f)

            agent_outputs = []
            for agent_name in ["vc", "lean", "cto", "ux", "regulator", "adversarial"]:
                agent_path = FIXTURES_DIR / f"agent_{agent_name}.json"
                if agent_path.exists():
                    with open(agent_path, "r", encoding="utf-8") as f:
                        agent_outputs.append(json.load(f))

            data = {
                "status": "complete",
                "investor_score": inv.get("score", 84),
                "confidence_band": inv.get("confidence_band", "fundable"),
                "score": inv.get("score", 84),
                "sections_count": len(brd.get("sections", [])),
                "sections": brd.get("sections", []),
                "brd": brd,
                "heatmap": hm,
                "pivots": [],
                "agent_outputs": agent_outputs,
                "score_matrix": sm,
                "project_name": "PRISM Automated SAST Code Review",
                "is_cached": True,
            }
            with open(b2b_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info("preseeded_b2b_cache", path=str(b2b_file))
        except Exception as e:
            logger.warning("failed_to_preseed_b2b_cache", error=str(e))

    # Helper for creating agent mock dicts
    def make_agent(name, role, score, focus, quote):
        return {
            "agent_name": name,
            "role": role,
            "persona": name,
            "score": score,
            "confidence": 0.88,
            "failed": False,
            "analysis": f"{quote} Focus: {focus}",
            "sections": [
                {
                    "title": f"{name.upper()} Assessment",
                    "content": f"{quote} Recommendation emphasizes {focus}.",
                    "lineage": {"source_agent": name, "confidence": 0.88, "data_citation": f"[SOURCE: {name}_analysis]"}
                }
            ],
            "strengths": [f"High alignment with {focus}", "Clear market niche"],
            "vulnerabilities": ["Execution dependency", "Regulatory friction"],
            "assumptions": ["Market adoption follows linear projections"]
        }

    # 2. P2P Social Lending (Scenario 2: Pivot Suggester Trigger)
    p2p_file = CACHE_DIR / "p2p_social_lending.json"
    if not p2p_file.exists():
        try:
            p2p_data = {
                "status": "complete",
                "investor_score": 48,
                "confidence_band": "needs_pivot",
                "score": 48,
                "sections_count": 6,
                "project_name": "KiteLend P2P Social Micro-Credit",
                "is_cached": True,
                "sections": [
                    {
                        "title": "Executive Summary & Viability",
                        "content": "P2P consumer micro-lending across Southeast Asian social networks addresses a $32B unbanked credit gap. However, unregulated viral origination exhibits severe credit default risk (estimated 38% non-performing loan rate) without collateralized anchors.",
                        "lineage": {"source_agent": "vc", "confidence": 0.82, "data_citation": "[SOURCE: worldbank] SE Asia unbanked adult population stands at 44%"}
                    },
                    {
                        "title": "Credit Underwriting & Default Vulnerabilities",
                        "content": "Social graph profiling is highly susceptible to coordinated synthetic identity syndicates and bot rings. The Adversarial analysis demonstrates an 84% exploit probability of credit rotation loops where borrowers repay using adjacent peer accounts.",
                        "lineage": {"source_agent": "adversarial", "confidence": 0.94, "data_citation": "[SOURCE: fraud_benchmark] Peer lending loan-cycling default attacks"}
                    },
                    {
                        "title": "Financial Viability & Capital Burn",
                        "content": "A $50k bootstrap capital pool is mathematically depleted in month 3 under expected default distributions. The venture cannot survive on interest spreads without debt warehouse facilities or bank syndication.",
                        "lineage": {"source_agent": "lean", "confidence": 0.90, "data_citation": "[SOURCE: unit_economics] Breakeven requires minimum $2.4M lending float"}
                    },
                    {
                        "title": "Regulatory & Licensing Minefield",
                        "content": "OJK (Indonesia) and SEC (Philippines) enforce rigorous 2024 microfinance interest caps (max 0.3%/day) and mandatory capitalization reserves. Operating without full NBFC licensing triggers instant cease-and-desist sanctions.",
                        "lineage": {"source_agent": "regulator", "confidence": 0.95, "data_citation": "[SOURCE: ojk_guidelines] Rule No. 10/POJK.05/2022 on Fintech Lending"}
                    },
                    {
                        "title": "Borrower Experience & Social Pressure",
                        "content": "Social-reputation debt enforcement creates extreme user friction and harassment liability. App Store policies explicitly ban apps utilizing contact-list harvesting for collection pressure.",
                        "lineage": {"source_agent": "ux", "confidence": 0.91, "data_citation": "[SOURCE: google_play_policy] Personal loan app contact book access prohibition"}
                    },
                    {
                        "title": "Technical Architecture & Settlement",
                        "content": "Fast payment integration requires local e-wallet APIs (GoPay, GCash, PromptPay). Micro-loan settlement engine built on PostgreSQL with strict optimistic locking and KYC verification webhooks.",
                        "lineage": {"source_agent": "cto", "confidence": 0.88, "data_citation": "[SOURCE: payment_rails] Direct wallet disbursement latency <1200ms"}
                    }
                ],
                "heatmap": {
                    "agents": ["vc", "lean", "cto", "ux", "regulator", "adversarial"],
                    "sections": [
                        "Executive Summary",
                        "Credit Underwriting",
                        "Financial Viability",
                        "Regulatory & Licensing",
                        "Borrower Experience",
                        "Technical Architecture"
                    ],
                    "matrix": [
                        [45, 40, 70, 60, 30, 25],
                        [40, 35, 75, 55, 25, 20],
                        [50, 45, 65, 50, 35, 30],
                        [35, 30, 80, 45, 20, 15],
                        [48, 52, 70, 40, 42, 28],
                        [60, 55, 85, 65, 50, 40]
                    ],
                    "divergence_score": 78
                },
                "pivots": [
                    {
                        "title": "Merchant-Secured Supply Chain Factoring",
                        "rationale": "Shift from uncollateralized consumer loans to financing TikTok Shop / Shopee merchant inventory receivables with automatic platform escrow lockup. Reduces default risk from 38% to under 3.5%."
                    },
                    {
                        "title": "Bank-Partnered Lending-as-a-Service (LaaS)",
                        "rationale": "License the AI credit scoring algorithm to existing Tier-2 rural banks rather than lending off balance sheet. Eliminates regulatory capital reserve hurdles while generating high-margin SaaS revenue."
                    }
                ],
                "score_matrix": {
                    "vc": 45, "lean": 40, "cto": 74, "ux": 52, "regulator": 30, "adversarial": 25
                },
                "agent_outputs": [
                    make_agent("vc", "Venture Capital Partner", 45, "Capital Efficiency", "Unsecured peer lending without platform escrow is uninvestable in 2026."),
                    make_agent("lean", "Lean Startup Strategist", 40, "Runway & Breakeven", "$50k bootstrap capital will evaporate on first cohort defaults."),
                    make_agent("cto", "Chief Technology Officer", 74, "Architecture", "Mobile app with local e-wallet hooks is straightforward to build."),
                    make_agent("ux", "User Experience Lead", 52, "Friction & Safety", "Social enforcement mechanisms cross ethical and app store boundaries."),
                    make_agent("regulator", "Compliance & Regulatory Counsel", 30, "Licensing", "Strict OJK and central bank interest rate caps trigger immediate enforcement."),
                    make_agent("adversarial", "Adversarial Red Team", 25, "Fraud Vulnerabilities", "Syndicated loan-cycling rings will systematically drain lending pools.")
                ]
            }
            p2p_data["brd"] = {"session_id": "cached_p2p", "sections": p2p_data["sections"]}
            with open(p2p_file, "w", encoding="utf-8") as f:
                json.dump(p2p_data, f, indent=2)
            logger.info("preseeded_p2p_cache", path=str(p2p_file))
        except Exception as e:
            logger.warning("failed_to_preseed_p2p_cache", error=str(e))

    # 3. Rural Telehealth AI (Scenario 3: Regulated HealthTech)
    telehealth_file = CACHE_DIR / "rural_telehealth.json"
    if not telehealth_file.exists():
        try:
            telehealth_data = {
                "status": "complete",
                "investor_score": 81,
                "confidence_band": "fundable",
                "score": 81,
                "sections_count": 6,
                "project_name": "DishaHealth AI: Rural Clinical Triage",
                "is_cached": True,
                "sections": [
                    {
                        "title": "Executive Summary & Clinical Need",
                        "content": "Rural healthcare in India faces a 1:11,000 doctor-to-patient deficit in primary health centres. DishaHealth equips community ASHA health workers with offline-capable AI diagnostic support, prioritizing emergency maternal and cardiovascular escalations.",
                        "lineage": {"source_agent": "vc", "confidence": 0.89, "data_citation": "[SOURCE: who_bulletin] Rural primary triage reduces clinical mortality by 42%"}
                    },
                    {
                        "title": "Clinical Triage & Differential Diagnosis",
                        "content": "Multimodal diagnostic assistant guides community health workers through structured symptom trees and optical image capture. System acts strictly as decision-support, mandating physician tele-consultation before prescription.",
                        "lineage": {"source_agent": "ux", "confidence": 0.88, "data_citation": "[SOURCE: aiims_guidelines] Clinical protocol for non-physician rural triage"}
                    },
                    {
                        "title": "DISHA & DPDP Act Data Governance",
                        "content": "Strict compliance with India's Digital Personal Data Protection (DPDP) Act 2023 and DISHA standards. Zero cross-border health telemetry; all patient identifiers are tokenized locally on-device and stored in certified Indian sovereign cloud regions.",
                        "lineage": {"source_agent": "regulator", "confidence": 0.94, "data_citation": "[SOURCE: dpdp_act_2023] Section 9: Processing of sensitive personal health data"}
                    },
                    {
                        "title": "Offline-First Edge Architecture",
                        "content": "ASHA tablets operate in intermittent 2G/zero-connectivity environments. Quantized ONNX triage models (under 120MB) execute on Android NPU, synchronizing encrypted differentials to central servers once network connectivity is re-established.",
                        "lineage": {"source_agent": "cto", "confidence": 0.93, "data_citation": "[SOURCE: edge_ai_benchmarks] 180ms inference latency on low-cost MediaTek chipsets"}
                    },
                    {
                        "title": "Unit Economics & Grant Co-Financing",
                        "content": "Priced at 25 INR ($0.30) per evaluated triage session, funded via state National Health Mission (NHM) allocations and CSR healthcare grants. 12-month pilot covers 45 Primary Health Centres.",
                        "lineage": {"source_agent": "lean", "confidence": 0.85, "data_citation": "[SOURCE: nhm_procurement] District digital health mission allocation guidelines"}
                    },
                    {
                        "title": "Adversarial Safety & Hallucination Mitigation",
                        "content": "Red team analysis tests medical hallucination rates under ambiguous symptom reports. Deterministic rule-based guardrails override LLM generation for red-flag vital signs (systolic BP >180, SpO2 <90%).",
                        "lineage": {"source_agent": "adversarial", "confidence": 0.91, "data_citation": "[SOURCE: medical_redteam] Deterministic fail-safe vital sign overrides"}
                    }
                ],
                "heatmap": {
                    "agents": ["vc", "lean", "cto", "ux", "regulator", "adversarial"],
                    "sections": [
                        "Executive Summary",
                        "Clinical Triage",
                        "DISHA & DPDP",
                        "Offline Edge",
                        "Unit Economics",
                        "Hallucination Safeguards"
                    ],
                    "matrix": [
                        [82, 80, 85, 88, 86, 75],
                        [80, 78, 88, 92, 85, 78],
                        [85, 75, 90, 82, 94, 82],
                        [78, 82, 95, 86, 88, 80],
                        [84, 86, 80, 80, 82, 74],
                        [80, 76, 88, 84, 90, 88]
                    ],
                    "divergence_score": 18
                },
                "pivots": [],
                "score_matrix": {
                    "vc": 82, "lean": 79, "cto": 88, "ux": 86, "regulator": 88, "adversarial": 80
                },
                "agent_outputs": [
                    make_agent("vc", "Venture Capital Partner", 82, "Impact Investing", "Strong alignment with global health impact funds and government procurement."),
                    make_agent("lean", "Lean Startup Strategist", 79, "Grant Runway", "NHM integration provides non-dilutive grant cushion during pilot phase."),
                    make_agent("cto", "Chief Technology Officer", 88, "Edge Architecture", "Quantized local models on Android tablets solve the 2G rural reality."),
                    make_agent("ux", "User Experience Lead", 86, "Voice & Iconography", "Simple regional-language voice prompts empower ASHA healthcare workers."),
                    make_agent("regulator", "Compliance & Regulatory Counsel", 88, "Data Privacy", "Local tokenization and sovereign hosting strictly satisfy DPDP 2023 mandates."),
                    make_agent("adversarial", "Adversarial Red Team", 80, "Clinical Boundaries", "Deterministic override thresholds effectively eliminate hallucination risk.")
                ]
            }
            telehealth_data["brd"] = {"session_id": "cached_telehealth", "sections": telehealth_data["sections"]}
            with open(telehealth_file, "w", encoding="utf-8") as f:
                json.dump(telehealth_data, f, indent=2)
            logger.info("preseeded_telehealth_cache", path=str(telehealth_file))
        except Exception as e:
            logger.warning("failed_to_preseed_telehealth_cache", error=str(e))

    # 4. Global PayTech AI (Scenario 4: Multi-Border FinCEN)
    paytech_file = CACHE_DIR / "global_paytech.json"
    if not paytech_file.exists():
        try:
            paytech_data = {
                "status": "complete",
                "investor_score": 79,
                "confidence_band": "fundable",
                "score": 79,
                "sections_count": 6,
                "project_name": "NexusPay Autonomous MiCA/FinCEN Compliance",
                "is_cached": True,
                "sections": [
                    {
                        "title": "Executive Summary & Market Imperative",
                        "content": "Cross-border B2B transactions incur $14B annually in compliance delays and false-positive sanctions freezes. NexusPay orchestrates real-time regulatory mapping between EU Markets in Crypto-Assets (MiCA) and US FinCEN guidelines.",
                        "lineage": {"source_agent": "vc", "confidence": 0.87, "data_citation": "[SOURCE: bis_report] Cross-border payment friction costs 2.4% of total transaction value"}
                    },
                    {
                        "title": "Dual-Jurisdiction Regulatory Engine",
                        "content": "Autonomous parser reconciles EU MiCA whitepaper authorization requirements with FinCEN Suspicious Activity Report (SAR) thresholds. Dynamic sanctions filtering against OFAC, EU Consolidated, and UN lists in under 45ms.",
                        "lineage": {"source_agent": "regulator", "confidence": 0.95, "data_citation": "[SOURCE: mica_regulation] EU 2023/1114 Titles III and IV compliance mandates"}
                    },
                    {
                        "title": "High-Throughput Streaming Infrastructure",
                        "content": "Event-driven Apache Kafka pipeline deployed across redundant multi-region AWS and GCP VPCs. Real-time transaction graph inspection utilizes distributed Graph Neural Networks for AML anomaly detection with sub-100ms P99 latency.",
                        "lineage": {"source_agent": "cto", "confidence": 0.91, "data_citation": "[SOURCE: latency_benchmarks] 12,000 TPS sustained transaction validation capacity"}
                    },
                    {
                        "title": "Enterprise Sales & Implementation Cycle",
                        "content": "Enterprise SaaS pricing structured at $3,500/month platform tier + $0.04 per cleared transaction. Targeted at tier-2 banks, neo-brokers, and multi-currency treasury platforms.",
                        "lineage": {"source_agent": "lean", "confidence": 0.83, "data_citation": "[SOURCE: banking_benchmark] Average bank compliance software spend up 26% YoY"}
                    },
                    {
                        "title": "Compliance Officer Copilot UX",
                        "content": "Audit-ready web console surfaces explainable AI decision paths for flagged transactions. One-click SAR draft generation eliminates 4 hours of manual case documentation per escalation.",
                        "lineage": {"source_agent": "ux", "confidence": 0.86, "data_citation": "[SOURCE: fatf_guidance] Explainability standards for automated AML reporting"}
                    },
                    {
                        "title": "Evasion & Smurfing Adversarial Testing",
                        "content": "Red team stress-tests cross-border 'smurfing' (splitting transactions under the $10,000 FinCEN reporting threshold). Temporal graph aggregation successfully links structured transactions across distributed wallets.",
                        "lineage": {"source_agent": "adversarial", "confidence": 0.89, "data_citation": "[SOURCE: aml_typologies] Structuring and smurfing pattern recognition"}
                    }
                ],
                "heatmap": {
                    "agents": ["vc", "lean", "cto", "ux", "regulator", "adversarial"],
                    "sections": [
                        "Executive Summary",
                        "Dual Regulatory Engine",
                        "Streaming Infra",
                        "Enterprise GTM",
                        "Compliance Officer UX",
                        "Smurfing Red Team"
                    ],
                    "matrix": [
                        [80, 78, 82, 85, 84, 76],
                        [82, 75, 88, 80, 95, 84],
                        [76, 80, 92, 82, 88, 82],
                        [85, 82, 78, 84, 80, 75],
                        [80, 79, 85, 90, 86, 78],
                        [78, 77, 88, 80, 90, 89]
                    ],
                    "divergence_score": 22
                },
                "pivots": [],
                "score_matrix": {
                    "vc": 80, "lean": 78, "cto": 86, "ux": 84, "regulator": 92, "adversarial": 83
                },
                "agent_outputs": [
                    make_agent("vc", "Venture Capital Partner", 80, "Enterprise FinTech", "Massive expansion in digital asset compliance spend across international banks."),
                    make_agent("lean", "Lean Startup Strategist", 78, "Sales Velocity", "Long enterprise procurement cycles (6-9 months) require conservative runway."),
                    make_agent("cto", "Chief Technology Officer", 86, "Streaming Scalability", "Kafka and Graph NN stack easily handles 10k+ TPS transaction load."),
                    make_agent("ux", "User Experience Lead", 84, "Explainable AI", "Audit trace visualization provides immediate trust for compliance officers."),
                    make_agent("regulator", "Compliance & Regulatory Counsel", 92, "Cross-Border MiCA", "Dual-jurisdiction crosswalk provides defensible compliance safe harbors."),
                    make_agent("adversarial", "Adversarial Red Team", 83, "Smurfing Detection", "Temporal graph linking reliably uncovers distributed smurfing rings.")
                ]
            }
            paytech_data["brd"] = {"session_id": "cached_paytech", "sections": paytech_data["sections"]}
            with open(paytech_file, "w", encoding="utf-8") as f:
                json.dump(paytech_data, f, indent=2)
            logger.info("preseeded_paytech_cache", path=str(paytech_file))
        except Exception as e:
            logger.warning("failed_to_preseed_paytech_cache", error=str(e))


def get_cached_run(text: str) -> dict[str, Any] | None:
    """Retrieve cached pipeline result by idea text or preset key."""
    _ensure_preseeded_fixtures()
    key = get_preset_key(text)
    file_path = CACHE_DIR / f"{key}.json"

    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cached_data["is_cached"] = True
                cached_data["preset_key"] = key
                return cached_data
        except Exception as e:
            logger.warning("failed_to_read_preset_cache", key=key, error=str(e))

    return None


def save_cached_run(text: str, result_dict: dict[str, Any]) -> str:
    """Save completed run into disk cache for instant demo replay."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = get_preset_key(text)
    file_path = CACHE_DIR / f"{key}.json"

    try:
        clean_data = dict(result_dict)
        clean_data["is_cached"] = True
        clean_data["preset_key"] = key
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=2)
        logger.info("saved_preset_cache", key=key, path=str(file_path))
        return key
    except Exception as e:
        logger.warning("failed_to_save_preset_cache", key=key, error=str(e))
        return key


def get_all_cached_status() -> dict[str, bool]:
    """Returns mapping of known presets to whether a cached run is ready."""
    _ensure_preseeded_fixtures()
    status = {}
    for preset_name in KNOWN_PRESETS:
        file_path = CACHE_DIR / f"{preset_name}.json"
        status[preset_name] = file_path.exists()
    return status
