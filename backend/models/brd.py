"""backend/models/brd.py — Pydantic models for the final merged BRD and lineage tags."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from backend.models.agents import AgentName, SectionName


class LineageTag(BaseModel):
    """Metadata tag tracking section origin agent, confidence, and data citations."""

    source_agent: AgentName
    agent_score: float = Field(..., ge=0.0, le=100.0)
    data_citations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=100.0)


class AssumptionFlag(BaseModel):
    """Hidden assumption surfaced from the BRD."""

    text: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    evidence: str
    action: str


class DissentNote(BaseModel):
    """Disagreement note from a competing agent on a specific section."""

    agent: AgentName
    key_disagreement: str


class FailureMode(BaseModel):
    """Failure mode simulation entry from Agent 6 (Adversarial)."""

    title: str
    probability_pct: float = Field(..., ge=0.0, le=100.0)
    description: str
    mitigation: str


class BRDSection(BaseModel):
    """Final merged BRD section with lineage, assumptions, and dissenting views."""

    content: str
    lineage: LineageTag
    assumptions: List[AssumptionFlag] = Field(default_factory=list)
    dissenting_agents: List[DissentNote] = Field(default_factory=list)
    failure_modes: List[FailureMode] = Field(default_factory=list)


class HeatmapSummary(BaseModel):
    """Summary of highest and lowest risk sections from the heatmap."""

    highest_risk_section: str
    lowest_risk_section: str


class MergedBRD(BaseModel):
    """Complete synthesised BRD output with section lineage and risk data."""

    session_id: str
    generated_at: str
    sections: Dict[SectionName, BRDSection]
    investor_readiness_score: float = Field(..., ge=0.0, le=100.0)
    investor_readiness_gaps: List[str] = Field(default_factory=list)
    heatmap_summary: HeatmapSummary
