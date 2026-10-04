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
    print("\n── NewsAPI Pre-warm ─────────────────────────────")
    print(f"Pre-warming {len(PREWARM_PAIRS)} scenario pairs...")
    await prewarm_cache(PREWARM_PAIRS)
    print("Pre-warm complete. NewsAPI cache populated for demo.")
    print("────────────────────────────────────────────────\n")


def _print_demo_talking_points(scenario) -> None:
    print(f"\n── Demo Talking Points for {scenario.name} ──")
    for i, point in enumerate(scenario.demo_talking_points, 1):
        print(f"  {i}. {point}")
    print()


async def run_scenario(scenario_name: str) -> None:
    from demo_config import DEMO_SCENARIOS, SCENARIOS_BY_NAME
    from config import init_vertex_ai

    scenario = SCENARIOS_BY_NAME.get(scenario_name)
    if scenario is None:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available: {[s.name for s in DEMO_SCENARIOS]}")
        sys.exit(1)

    session_id = f"{scenario.session_id_prefix}-{str(uuid.uuid4())[:8]}"

    print(f"\n{'═'*55}")
    print(f"  PRISM Demo Runner — {scenario.name}")
    print(f"{'═'*55}")
    print(f"  Session:  {session_id}")
    print(f"  Region:   {scenario.extraction.region}")
    print(f"  Industry: {scenario.extraction.industry}")
    print(f"  Stage:    {scenario.extraction.stage}")
    print(f"  Budget:   {scenario.extraction.budget_range}")
    print(f"{'─'*55}")

    # Init Vertex AI
    try:
        init_vertex_ai()
        print("  ✓ Vertex AI initialised")
    except Exception as e:
        print(f"  ✗ Vertex AI init failed: {type(e).__name__}")
        print("    Running in dev mode — pipeline will stop at first Gemini call")

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
