from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    incident: str = Field(min_length=1, max_length=2000)


class TriageDecision(BaseModel):
    category: str
    priority: str
    summary: str
    requires_human_review: bool


class TriageResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    category: str
    priority: str
    summary: str
    requires_human_review: bool
    duration_ms: int = Field(default=0, ge=0)


class RunEvidence(BaseModel):
    id: UUID
    created_at: datetime
    provider: str
    model: str | None
    category: str
    priority: str
    requires_human_review: bool
    duration_ms: int
