"""
PRISM Demo Runner — end-to-end dry-run script.

Usage:
    python demo_runner.py                        # runs IndiaFintechSMB scenario
    python demo_runner.py SingaporeEdTechB2B     # runs named scenario
    python demo_runner.py --list                 # lists all scenarios
    python demo_runner.py --prewarm              # pre-warms NewsAPI cache only

With real GCP credentials: runs the full pipeline and prints the investor score.
Without GCP (dev mode): runs up to the Vertex AI call and reports cleanly.
"""

import asyncio
import os
import sys
import time
import uuid
import structlog

# Ensure backend/ is on path when run directly
sys.path.insert(0, os.path.dirname(__file__))

from logging_config import configure_logging
configure_logging()
logger = structlog.get_logger()


async def prewarm_only() -> None:
    from context.newsapi import prewarm_cache
    from demo_config import PREWARM_PAIRS
    print("\n-- NewsAPI Pre-warm -----------------------------")
    print(f"Pre-warming {len(PREWARM_PAIRS)} scenario pairs...")
    await prewarm_cache(PREWARM_PAIRS)
    print("Pre-warm complete. NewsAPI cache populated for demo.")
    print("------------------------------------------------\n")


def _print_demo_talking_points(scenario) -> None:
    print(f"\n-- Demo Talking Points for {scenario.name} --")
    for i, point in enumerate(scenario.demo_talking_points, 1):
        print(f"  {i}. {point}")
    print()


async def run_scenario(scenario_name: str) -> None:
    from demo_config import DEMO_SCENARIOS, SCENARIOS_BY_NAME
    from config import init_vertex_ai, settings

    scenario = SCENARIOS_BY_NAME.get(scenario_name)
    if scenario is None:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available: {[s.name for s in DEMO_SCENARIOS]}")
        sys.exit(1)

    session_id = f"{scenario.session_id_prefix}-{str(uuid.uuid4())[:8]}"

    print(f"\n{'='*55}")
    print(f"  PRISM Demo Runner — {scenario.name}")
    print(f"{'='*55}")
    print(f"  Session:  {session_id}")
    print(f"  Region:   {scenario.extraction.region}")
    print(f"  Industry: {scenario.extraction.industry}")
    print(f"  Stage:    {scenario.extraction.stage}")
    print(f"  Budget:   {scenario.extraction.budget_range}")
    print(f"{'-'*55}")

    # Init Vertex AI
    try:
        init_vertex_ai()
        print("  [OK] Vertex AI initialised")
    except Exception as e:
        print(f"  [X] Vertex AI init failed: {type(e).__name__}")
        print("    Running in dev mode — pipeline will stop at first Gemini call")

    # Step 1: Context harvest
    print("\n[1/6] Context harvest...")
    start = time.time()
    from models.intake import IntakePackage
    from datetime import datetime, timezone
    from context.harvester import harvest_context

    intake = IntakePackage(
        session_id=session_id,
        extraction=scenario.extraction,
        created_at=datetime.now(timezone.utc),
    )

    context = await harvest_context(intake)
    elapsed = int((time.time() - start) * 1000)
    print(f"      [OK] {elapsed}ms | news:{len(context.news_items)} market:{context.market_data is not None} regs:{len(context.regulatory_flags)} flags:{len(context.failed_sources)} failed")

    # Step 2: Build agent prompts (no Vertex AI yet)
    print("\n[2/6] Building agent prompts...")
    from agents.prompts import build_agent_prompt
    from models.agents import AgentPersona
    from agents.personas import PERSONAS

    prompt_sizes = {}
    for persona in AgentPersona:
        prompt = build_agent_prompt(persona, intake, context)
        prompt_sizes[persona.value] = len(prompt)
    print(f"      [OK] 6 prompts built | sizes: {prompt_sizes}")

    # Step 3: Swarm (will fail without GCP — expected in dev)
    print("\n[3/6] Running 6-agent swarm (requires GCP)...")
    start = time.time()
    from agents.swarm import run_swarm
    from errors import SwarmError

    agent_outputs = []
    try:
        agent_outputs = await run_swarm(intake, context, session_id)
        successful = [o for o in agent_outputs if not o.failed]
        elapsed = int((time.time() - start) * 1000)
        print(f"      [OK] {elapsed}ms | {len(successful)}/6 agents succeeded")
        for o in agent_outputs:
            status = "[OK]" if not o.failed else "[X]"
            dur = o.duration_ms or 0
            print(f"        {status} {o.agent.value:<12} {dur}ms")
    except SwarmError as e:
        print(f"      [X] Swarm failed: {e.message}")
        print("        This is expected in dev mode without GCP credentials.")
        print("        With real credentials this step takes ~20s.")
        _print_demo_talking_points(scenario)
        return
    except Exception as e:
        print(f"      [X] {type(e).__name__}: {e}")
        _print_demo_talking_points(scenario)
        return

    # Step 4: Evaluate
    print("\n[4/6] Evaluating BRDs with Gemini Pro...")
    start = time.time()
    from evaluation.evaluator import evaluate_all_agents

    try:
        score_matrix = await evaluate_all_agents(agent_outputs, context)
        elapsed = int((time.time() - start) * 1000)
        print(f"      [OK] {elapsed}ms | winning agent: {score_matrix.winning_agent.value if score_matrix.winning_agent else 'none'}")
        for agent_key, score in score_matrix.scores.items():
            print(f"        {agent_key:<12} composite={score.composite:.1f}")
    except Exception as e:
        print(f"      [X] Evaluation failed: {type(e).__name__}")
        return

    # Step 5: Merge
    print("\n[5/6] Merging BRDs with Gemini Pro...")
    start = time.time()
    from evaluation.merger import merge_brds

    try:
        merged_brd = await merge_brds(agent_outputs, score_matrix, context)
        elapsed = int((time.time() - start) * 1000)
        print(f"      [OK] {elapsed}ms | {len(merged_brd.sections)} sections merged")
    except Exception as e:
        print(f"      [X] Merge failed: {type(e).__name__}")
        return

    # Step 6: Output layer
    print("\n[6/6] Computing output layer...")
    from output.heatmap import calculate_heatmap
    from output.investor_score import calculate_investor_score
    from output.pivot import suggest_pivots

    heatmap = calculate_heatmap(score_matrix)
    investor_score = calculate_investor_score(score_matrix)
    pivots = await suggest_pivots(merged_brd, investor_score)

    print(f"\n{'='*55}")
    print(f"  PRISM RESULT - {scenario.name}")
    print(f"{'='*55}")
    print(f"  Investor Readiness Score: {investor_score.score}/100 ({investor_score.confidence_band})")
    print(f"  Gap flags:  {len(investor_score.gap_flags)}")
    for g in investor_score.gap_flags:
        print(f"    * {g.criterion} ({g.score}/100): {g.action_item}")
    print(f"  Heatmap risk bars:")
    for b in heatmap.bars:
        bar = "#" * (b.risk_score // 10)
        print(f"    {b.section_title:<22} {bar:<10} {b.risk_score}/100")
    if pivots:
        print(f"  Pivot suggestions ({len(pivots)}):")
        for p in pivots:
            print(f"    -> {p.direction} (projected: {p.projected_score}/100)")
    else:
        print(f"  Pivot suggester: not triggered (score >= 60)")

    # Validate expected range
    lo, hi = scenario.expected_score_range
    in_range = lo <= investor_score.score <= hi
    print(f"\n  Expected range: {lo}-{hi} | Actual: {investor_score.score} | {'[OK] IN RANGE' if in_range else '[X] OUT OF RANGE'}")
    print(f"{'='*55}\n")

    _print_demo_talking_points(scenario)


async def main() -> None:
    args = sys.argv[1:]

    if "--list" in args:
        from demo_config import DEMO_SCENARIOS
        print("\nAvailable PRISM demo scenarios:")
        for s in DEMO_SCENARIOS:
            lo, hi = s.expected_score_range
            print(f"  {s.name:<25} region={s.extraction.region} industry={s.extraction.industry} expected={lo}-{hi}")
        print()
        return

    if "--prewarm" in args:
        await prewarm_only()
        return

    scenario_name = args[0] if args else "IndiaFintechSMB"
    await run_scenario(scenario_name)


if __name__ == "__main__":
    asyncio.run(main())
