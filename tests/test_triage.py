from fastapi.testclient import TestClient

from inference_gateway.main import app

client = TestClient(app)


def test_subtitle_incident_is_triaged_for_review() -> None:
    response = client.post(
        "/v1/triage",
        json={
            "incident": "My subtitles vanished halfway through Neon Harbour.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "rules-baseline"
    assert body["model"] == "relay-rules-v1"
    assert body["category"] == "playback"
    assert body["priority"] == "normal"
    assert body["requires_human_review"] is True
    assert body["summary"]
    assert body["request_id"]


def test_triage_of_incident_with_missing_value() -> None:
    response = client.post("/v1/triage", json={})

    assert response.status_code == 422


def test_triage_of_incident_with_oversized_value() -> None:
    response = client.post(
        "/v1/triage",
        json={
            "incident": "a" * 2001,
        },
    )
    assert response.status_code == 422


def test_triage_of_incident_with_whitespace_only() -> None:
    response = client.post("/v1/triage", json={"incident": "      "})
    assert response.status_code == 422
