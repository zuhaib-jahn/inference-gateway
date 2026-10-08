import os
from collections.abc import Callable
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Engine, create_engine

from inference_gateway.providers.rules import RulesBaselineProvider
from inference_gateway.schemas import RunEvidence, TriageRequest, TriageResponse
from inference_gateway.services.triage import TriageService
from inference_gateway.storage import get_result, save_result


def get_provider() -> RulesBaselineProvider:
    return RulesBaselineProvider()


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(
        os.environ["DATABASE_URL"],
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )


def get_writer(engine: Engine = Depends(get_engine)):
    def write(values: dict[str, object]):
        save_result(engine, values)

    return write


app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/results/{request_id}", response_model=RunEvidence)
def retrieve(request_id: UUID, engine: Engine = Depends(get_engine)):
    result: dict[str, object] | None = get_result(engine, str(request_id))
    if result is None:
        raise HTTPException(status_code=404)
    run = RunEvidence.model_validate(result)
    return run


@app.post("/v1/triage", response_model=TriageResponse)
def triage(
    request: TriageRequest,
    provider: Annotated[RulesBaselineProvider, Depends(get_provider)],
    writer: Annotated[Callable[[dict[str, object]], None], Depends(get_writer)],
) -> TriageResponse:
    service = TriageService(provider)

    try:
        return service.triage(request, save_record=writer)
    except ValueError as vle:
        raise HTTPException(status_code=422, detail=str(vle)) from vle
