from collections.abc import Callable
from time import perf_counter
from uuid import UUID, uuid4

from inference_gateway.schemas import TriageDecision, TriageRequest, TriageResponse


class TriageService:
    def __init__(self, provider) -> None:
        self.provider = provider

    def triage(
        self, request: TriageRequest, save_record: Callable[[dict], None] | None = None
    ) -> TriageResponse:
        if not request.incident.strip():
            raise ValueError("Incident must contain non-whitespace characters")

        request_id = str(uuid4())
        start = perf_counter()
        raw_decision = self.provider.triage(request.incident)
        duration_ms = int((perf_counter() - start) * 1000)
        decision = TriageDecision.model_validate(raw_decision)

        response = TriageResponse(
            request_id=request_id,
            provider=self.provider.name,
            model=self.provider.model,
            category=decision.category,
            priority=decision.priority,
            summary=decision.summary,
            requires_human_review=decision.requires_human_review,
            duration_ms=duration_ms,
        )

        if save_record is not None:
            save_record(
                {
                    "id": UUID(response.request_id),
                    "provider": response.provider,
                    "model": response.model,
                    "category": response.category,
                    "priority": response.priority,
                    "requires_human_review": response.requires_human_review,
                    "duration_ms": response.duration_ms,
                }
            )

        return response
