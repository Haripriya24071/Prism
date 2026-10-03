"""backend/models/intake.py — Pydantic models for intake processing and requests."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


UUID4_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
ISO_REGION_PATTERN = r"^[A-Z]{2}$"


class SessionIdHeader(BaseModel):
    """Reusable model for validating UUID v4 session IDs."""

    session_id: str = Field(..., pattern=UUID4_PATTERN, description="UUID v4 session identifier")


class ConversationTurn(BaseModel):
    """Single turn in the conversational intake."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    """Request schema for submitting a conversational turn."""

    session_id: str = Field(..., pattern=UUID4_PATTERN)
    content: str = Field(..., min_length=1, max_length=5000)
    role: Literal["user"] = "user"


class ExtractedIntake(BaseModel):
    """Structured fields extracted from the intake conversation."""

    business_idea: str
    region: str = Field(..., pattern=ISO_REGION_PATTERN, description="ISO 3166-1 alpha-2 country code")
    industry: str = Field(..., max_length=100)
    stage: Optional[Literal["idea", "prototype", "mvp", "growth"]] = None
    budget_range: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)


class FileContext(BaseModel):
    """Extracted text and analysis from uploaded images and documents."""

    image_analyses: List[str] = Field(default_factory=list)
    document_summaries: List[str] = Field(default_factory=list)


class IntakePackage(BaseModel):
    """Unified intake package containing conversation, extracted fields, and context."""

    session_id: str = Field(..., pattern=UUID4_PATTERN)
    created_at: str
    conversation_turns: List[ConversationTurn] = Field(default_factory=list)
    extracted: ExtractedIntake
    file_contexts: FileContext = Field(default_factory=FileContext)
    context_package: Optional[dict] = None
