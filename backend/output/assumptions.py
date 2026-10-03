"""backend/output/assumptions.py — Scans BRD for hidden assumptions."""

from backend.models.brd import MergedBRD, AssumptionFlag
from backend.models.context import ContextPackage


async def flag_assumptions(merged_brd: MergedBRD, context: ContextPackage) -> list[AssumptionFlag]:
    raise NotImplementedError("Phase 9")
