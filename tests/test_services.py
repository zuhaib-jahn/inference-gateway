from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from inference_gateway.main import app, get_provider
from inference_gateway.schemas import TriageDecision, TriageRequest
from inference_gateway.services.triage import TriageService


class FakeProvider:
    name = "fake-provider"
    model = "fake-v1"

    def __init__(self) -> None:
        self.incident_list: list[str] = []

    def triage(self, incident: str) -> TriageDecision:
        self.incident_list.append(incident)
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


def test_dependency_override_with_fake_provier() -> None:
    fake = FakeProvider()

    app.dependency_overrides[get_provider] = lambda: fake
    try:
        client = TestClient(app)
        response = client.post("/v1/triage", json={"incident": "subtitle vanished"})
        body = response.json()
        assert fake.incident_list == ["subtitle vanished"]
        assert body["category"] == "sync"
        assert body["model"] == "fake-v1"
    finally:
        app.dependency_overrides.clear()


def test_triageservice_with_fake_save_function() -> None:
    fake = FakeProvider()
    saved = []

    def fake_save(record):
        saved.append(record)

    response = TriageService(fake).triage(
        TriageRequest(incident="Fake incident"), save_record=fake_save
    )

    record = saved[0]
    assert record["id"] == UUID(response.request_id)
    assert "incident" not in record
    assert "summary" not in record


def test_service_does_not_return_success_when_save_fails() -> None:
    fake = FakeProvider()

    def broken_save(record: dict) -> None:
        raise RuntimeError("save failed")

    with pytest.raises(RuntimeError):
        TriageService(fake).triage(
            TriageRequest(incident="Fake incident"),
            save_record=broken_save,
        )
