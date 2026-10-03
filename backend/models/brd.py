from pydantic import BaseModel, Field
from .agents import AgentPersona


class LineageTag(BaseModel):
    source_agent: AgentPersona
    confidence: float = Field(ge=0.0, le=1.0)
    data_citation: str


class BRDSection(BaseModel):
    title: str
    content: str
    lineage: LineageTag | None = None


class AssumptionFlag(BaseModel):
    assumption: str
    confidence: str = Field(description="high | medium | low")
    evidence: str | None = None
    recommended_action: str


class FailureMode(BaseModel):
    title: str
    probability_pct: int = Field(ge=0, le=100)
    description: str
    mitigation: str


class MergedBRD(BaseModel):
    session_id: str
    sections: list[BRDSection] = Field(default_factory=list)
    assumptions: list[AssumptionFlag] = Field(default_factory=list)
    failure_modes: list[FailureMode] = Field(default_factory=list)
    investor_readiness_score: int | None = None
