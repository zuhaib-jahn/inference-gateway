from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from inference_gateway.providers.rules import RulesBaselineProvider
from inference_gateway.schemas import TriageRequest, TriageResponse
from inference_gateway.services.triage import TriageService


def get_provider() -> RulesBaselineProvider:
    return RulesBaselineProvider()


app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/triage", response_model=TriageResponse)
def triage(
    request: TriageRequest,
    provider: Annotated[RulesBaselineProvider, Depends(get_provider)],
) -> TriageResponse:
    service = TriageService(provider)

    try:
        return service.triage(request)
    except ValueError as vle:
        raise HTTPException(status_code=422, detail=str(vle)) from vle
