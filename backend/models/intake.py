from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    session_id: Annotated[str, Field(min_length=8, pattern=r"^[a-zA-Z0-9_-]+$", description="Session UUID")]
    message: Annotated[str, Field(max_length=2000, description="User message — max 2000 chars")]
    turn_number: int = Field(ge=0, description="Zero-indexed conversation turn")


class UploadRequest(BaseModel):
    session_id: Annotated[str, Field(min_length=8, description="Session UUID")]
    file_type: Literal["image", "pdf", "doc"] = Field(description="Detected MIME category")


class IntakeExtraction(BaseModel):
    raw_idea: str = Field(description="Full unstructured idea text from conversation")
    region: str | None = Field(default=None, description="ISO 3166-1 alpha-2 country code")
    industry: str | None = Field(default=None, description="Industry vertical")
    stage: Literal["idea", "prototype", "mvp", "growth"] | None = Field(default=None)
    budget_range: str | None = Field(default=None)
    success_definition: str | None = Field(default=None)


class IntakePackage(BaseModel):
    model_config = ConfigDict(frozen=True)
    session_id: Annotated[str, Field(min_length=8)]
    extraction: IntakeExtraction
    file_context: str | None = Field(default=None, description="Text from uploaded file")
    conversation_history: list[dict] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
