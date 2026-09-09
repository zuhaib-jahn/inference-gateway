from fastapi import FastAPI, HTTPException

from inference_gateway.providers.rules import RulesBaselineProvider
from inference_gateway.schemas import TriageRequest, TriageResponse
from inference_gateway.services.triage import TriageService

app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/triage", response_model=TriageResponse)
async def triage(request: TriageRequest) -> TriageResponse:
    try:
        service = TriageService(RulesBaselineProvider())
    except ValueError as vle:
        raise HTTPException(status_code=422, detail=str(vle))

    return service.triage(request)
