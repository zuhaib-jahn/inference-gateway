import os
import uuid
from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError


@pytest.fixture
def engine() -> Generator[Engine]:
    test_db_url = os.environ["TEST_DATABASE_URL"]

    database_name = make_url(test_db_url).database

    if database_name is None or not database_name.endswith("_test"):
        pytest.fail("TEST_DATABASE_URL must point to a database ending in _test")

    engine = create_engine(
        test_db_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    yield engine

    engine.dispose()


def insert_result(engine: Engine, result_id: uuid.UUID, provider: str) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO results (
                    id,
                    provider,
                    model,
                    category,
                    priority,
                    requires_human_review,
                    duration_ms
                )
                VALUES (
                    :id,
                    :provider,
                    :model,
                    :category,
                    :priority,
                    :requires_human_review,
                    :duration_ms
                )
                """
            ),
            {
                "id": result_id,
                "provider": provider,
                "model": "fake-v1",
                "category": "sync",
                "priority": "normal",
                "requires_human_review": False,
                "duration_ms": 12,
            },
        )


def delete_result(engine: Engine, result_id: uuid.UUID) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM results WHERE id = :id"),
            {"id": result_id},
        )


def test_insert_and_fetch_result(engine: Engine) -> None:
    result_id = uuid.uuid4()

    try:
        insert_result(engine, result_id, "fake-provider")

        with engine.begin() as conn:
            row = (
                conn.execute(
                    text("SELECT id FROM results WHERE id = :id"),
                    {"id": result_id},
                )
                .mappings()
                .first()
            )

        assert row is not None
        assert row["id"] == result_id

    finally:
        delete_result(engine, result_id)


def test_missing_result_returns_none(engine: Engine) -> None:
    missing_id = uuid.uuid4()

    with engine.begin() as conn:
        row = (
            conn.execute(
                text("SELECT id FROM results WHERE id = :id"),
                {"id": missing_id},
            )
            .mappings()
            .first()
        )

    assert row is None


def test_duplicate_id_raises_integrity_error(engine: Engine) -> None:
    result_id = uuid.uuid4()

    try:
        insert_result(engine, result_id, "original-provider")

        with pytest.raises(IntegrityError):
            insert_result(engine, result_id, "different-provider")

        with engine.begin() as conn:
            row = (
                conn.execute(
                    text(
                        """
                        SELECT provider
                        FROM results
                        WHERE id = :id
                        """
                    ),
                    {"id": result_id},
                )
                .mappings()
                .first()
            )

        assert row is not None
        assert row["provider"] == "original-provider"

    finally:
        delete_result(engine, result_id)
