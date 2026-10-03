"""backend/context/harvester.py — Aggregates all 5 context sources in parallel."""

from backend.models.intake import IntakePackage
from backend.models.context import ContextPackage


async def harvest_context(intake: IntakePackage) -> ContextPackage:
    raise NotImplementedError("Phase 5")
