from pydantic import BaseModel, Field


class HeatmapBar(BaseModel):
    section_title: str
    risk_score: int = Field(ge=0, le=100, description="Normalised disagreement score — higher = riskier")
    std_dev: float


class HeatmapData(BaseModel):
    session_id: str
    bars: list[HeatmapBar]


class GapFlag(BaseModel):
    criterion: str
    score: int
    action_item: str


class InvestorScore(BaseModel):
    session_id: str
    score: int = Field(ge=0, le=100)
    confidence_band: str = Field(description="fundable | promising | needs_work")
    gap_flags: list[GapFlag] = Field(default_factory=list)


class PivotSuggestion(BaseModel):
    direction: str
    rationale: str
    projected_score: int = Field(ge=0, le=100)


class FinalOutput(BaseModel):
    session_id: str
    heatmap: HeatmapData | None = None
    investor_score: InvestorScore | None = None
    pivots: list[PivotSuggestion] = Field(default_factory=list)
    pdf_urls: dict[str, str] = Field(default_factory=dict, description="view -> signed GCS URL")
