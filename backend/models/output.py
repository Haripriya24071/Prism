"""backend/models/output.py — Pydantic models for heatmap, investor readiness score, pivots, and SSE events."""

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from backend.models.agents import AgentName, SectionName


RiskLevel = Literal["low", "medium", "high"]


class HeatmapItem(BaseModel):
    """Agreement score and risk level metrics for a single section across swarm agents."""

    section_name: SectionName
    agreement_score: float = Field(..., ge=0.0, le=100.0)
    std_deviation: float = Field(..., ge=0.0)
    risk_level: RiskLevel
    min_score: float = Field(..., ge=0.0, le=100.0)
    max_score: float = Field(..., ge=0.0, le=100.0)
    dominant_agent: AgentName


class HeatmapData(BaseModel):
    """Complete divergence heatmap payload."""

    session_id: str
    sections: List[HeatmapItem] = Field(default_factory=list)
    calculated_at: str


class PivotSuggestion(BaseModel):
    """Concrete pivot direction generated when investor readiness score < 60."""

    title: str
    description: str
    projected_score: float = Field(..., ge=0.0, le=100.0)
    key_changes: List[str] = Field(default_factory=list)


class InvestorReadiness(BaseModel):
    """Investor readiness composite score, gap breakdown, and pivot suggestions."""

    score: float = Field(..., ge=0.0, le=100.0)
    breakdown: Dict[str, float] = Field(default_factory=dict)
    gaps: List[str] = Field(default_factory=list)
    pivot_triggered: bool = False
    pivot_suggestions: List[PivotSuggestion] = Field(default_factory=list)


# --- SSE Event Payloads ---


class AgentStatusEvent(BaseModel):
    """SSE payload for agent status updates."""

    agent: AgentName
    status: Literal["pending", "running", "complete", "failed"]
    progress_pct: int = Field(..., ge=0, le=100)


class ContextReadyEvent(BaseModel):
    """SSE payload emitted when context harvester completes."""

    sources: List[str]
    progress_pct: int = Field(..., ge=0, le=100)


class EvaluationCompleteEvent(BaseModel):
    """SSE payload emitted when evaluator finishes scoring."""

    winning_agent: AgentName
    score: float = Field(..., ge=0.0, le=100.0)
    progress_pct: int = Field(..., ge=0, le=100)


class BrdReadyEvent(BaseModel):
    """SSE payload emitted when final merged BRD generation is complete."""

    session_id: str
    investor_readiness_score: float = Field(..., ge=0.0, le=100.0)
    progress_pct: int = 100
