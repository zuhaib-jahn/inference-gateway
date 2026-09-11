from uuid import uuid4

from inference_gateway.schemas import TriageRequest, TriageResponse


class TriageService:
    def __init__(self, provider) -> None:
        self.provider = provider

    def triage(self, request: TriageRequest) -> TriageResponse:
        if not request.incident.strip():
            raise ValueError("Incident must contain non-whitespace characters")
        decision = self.provider.triage(request.incident)
        return TriageResponse(
            request_id=str(uuid4()),
            provider=self.provider.name,
            model=self.provider.model,
            category=decision.category,
            priority=decision.priority,
            summary=decision.summary,
            requires_human_review=decision.requires_human_review,
        )
