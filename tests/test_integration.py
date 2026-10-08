import os
from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url

from inference_gateway.main import app, get_engine, get_writer
from inference_gateway.storage import get_result


@pytest.fixture
def test_engine() -> Generator[Engine]:
    test_db_url = os.environ["TEST_DATABASE_URL"]

    database_name = make_url(test_db_url).database

    if database_name is None or not database_name.endswith("_test"):
        pytest.fail("TEST_DATABASE_URL must point to a database ending in _test")

    test_engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    yield test_engine

    test_engine.dispose()


@pytest.fixture
def client(test_engine: Engine) -> Generator[TestClient]:
    app.dependency_overrides[get_engine] = lambda: test_engine
    client = TestClient(app)

    yield client

    app.dependency_overrides.clear()


def test_triage_post_persists_result_to_database(
    client: TestClient, test_engine: Engine
) -> None:

    response = client.post("/v1/triage", json={"incident": "subtitle vanished"})
    assert response.status_code == 200

    body = response.json()
    request_id = str(body["request_id"])

    result = get_result(test_engine, request_id)

    assert result is not None
    assert result["provider"] == body["provider"]
    assert result["category"] == body["category"]
    assert result["duration_ms"] == body["duration_ms"]


def test_if_triage_post_save_fails_does_not_return_success(client: TestClient) -> None:

    def get_broken_writer():
        def broken_writer(record: dict[str, object]) -> None:
            raise RuntimeError("save failed")

        return broken_writer

    app.dependency_overrides[get_writer] = get_broken_writer

    with pytest.raises(RuntimeError):
        client.post("/v1/triage", json={"incident": "subtitle vanished"})


def test_retrieve_run_evidence(client: TestClient) -> None:

    response = client.post("/v1/triage", json={"incident": "subtitle vanished"})
    assert response.status_code == 200
    post_body = response.json()
    stored_id = post_body["request_id"]

    run = client.get(f"/v1/results/{UUID(stored_id)}")
    assert run.status_code == 200
    get_body = run.json()

    assert get_body["id"] == post_body["request_id"]
    assert get_body["model"] == post_body["model"]
    assert get_body["category"] == post_body["category"]


def test_retrieve_run_with_non_existing_id(client: TestClient) -> None:
    fake_id = uuid4()

    response = client.get(f"/v1/results/{fake_id}")
    assert response.status_code == 404


def test_retrieve_run_with_malformed_id(client: TestClient) -> None:
    fake_id = "NOTANID"

    response = client.get(f"/v1/results/{fake_id}")
    assert response.status_code == 422
