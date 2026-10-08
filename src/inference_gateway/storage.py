from sqlalchemy import Engine, text


def save_result(engine: Engine, values: dict[str, object]) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO results (id, provider, model, category, priority, requires_human_review, duration_ms)"
                " VALUES (:id, :provider, :model, :category, :priority, :requires_human_review, :duration_ms)"
            ),
            {
                "id": values["id"],
                "provider": values["provider"],
                "model": values["model"],
                "category": values["category"],
                "priority": values["priority"],
                "requires_human_review": values["requires_human_review"],
                "duration_ms": values["duration_ms"],
            },
        )


def get_result(engine: Engine, id: str) -> dict[str, object] | None:
    with engine.begin() as conn:
        row = (
            conn.execute(
                text("SELECT * FROM results WHERE id = :id"),
                {"id": id},
            )
            .mappings()
            .first()
        )

        if not row:
            return None
        return dict(row)
