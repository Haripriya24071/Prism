import sys

if "backend.models.agents" in sys.modules and "models.agents" not in sys.modules:
    sys.modules["models.agents"] = sys.modules["backend.models.agents"]
elif "models.agents" in sys.modules and "backend.models.agents" not in sys.modules:
    sys.modules["backend.models.agents"] = sys.modules["models.agents"]

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class AgentPersona(str, Enum):
    VC = "vc"
    LEAN_FOUNDER = "lean"
    ENTERPRISE_CTO = "cto"
    UX_RESEARCHER = "ux"
    REGULATOR = "regulator"
    ADVERSARIAL = "adversarial"


class AgentOutput(BaseModel):
    agent: AgentPersona
    brd_json: dict = Field(default_factory=dict, description="Structured BRD sections from this agent")
    raw_text: str = Field(default="", description="Raw Vertex AI response — kept for debugging")
    completed_at: datetime | None = None
    duration_ms: int | None = None
    failed: bool = Field(default=False)


class SectionScore(BaseModel):
    feasibility: int = Field(ge=0, le=100)
    market_timing: int = Field(ge=0, le=100)
    regulatory_safety: int = Field(ge=0, le=100)
    user_adoption: int = Field(ge=0, le=100)
    competitive_moat: int = Field(ge=0, le=100)
    composite: float = Field(ge=0, le=100)
    data_citation: str = Field(description="One-line evidence backing this score")


class ScoreMatrix(BaseModel):
    session_id: str
    scores: dict[str, SectionScore] = Field(description="Keyed by AgentPersona value string")
    winning_agent: AgentPersona | None = None
