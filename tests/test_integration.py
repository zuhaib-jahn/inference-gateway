import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine

from inference_gateway.main import app, get_engine, get_writer
from inference_gateway.storage import get_result


def test_triage_post_persists_result_to_database() -> None:
    test_engine: Engine = create_engine(
        os.environ["TEST_DATABASE_URL"],
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    app.dependency_overrides[get_engine] = lambda: test_engine
    client = TestClient(app)

    try:
        response = client.post("/v1/triage", json={"incident": "subtitle vanished"})
        assert response.status_code == 200

        body = response.json()
        request_id = str(body["request_id"])

        result = get_result(test_engine, request_id)

        assert result is not None
        assert result["provider"] == body["provider"]
        assert result["category"] == body["category"]
        assert result["duration_ms"] == body["duration_ms"]

    finally:
        test_engine.dispose()
        app.dependency_overrides.clear()


def test_if_triage_post_save_fails_does_not_return_success() -> None:

    def get_broken_writer():
        def broken_writer(record: dict[str, object]) -> None:
            raise RuntimeError("save failed")

        return broken_writer

    app.dependency_overrides[get_writer] = get_broken_writer
    client = TestClient(app)

    try:
        with pytest.raises(RuntimeError):
            client.post("/v1/triage", json={"incident": "subtitle vanished"})
    finally:
        app.dependency_overrides.clear()
