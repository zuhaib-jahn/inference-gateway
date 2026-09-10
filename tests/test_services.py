from inference_gateway.schemas import TriageDecision, TriageRequest
from inference_gateway.services.triage import TriageService


class FakeProvider:
    name = "fake-provider"
    model = "fake-v1"

    def triage(self, incident: str) -> TriageDecision:
        return TriageDecision(
            category="sync",
            priority="normal",
            summary="Fake Summary",
            requires_human_review=False,
        )


def test_service_with_fake_provider() -> None:
    fake = FakeProvider()
    service_response = TriageService(fake).triage(
        TriageRequest(incident="Fake incident")
    )
    assert service_response.request_id
    assert service_response.provider == "fake-provider"
    assert service_response.model == "fake-v1"
