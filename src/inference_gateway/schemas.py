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
