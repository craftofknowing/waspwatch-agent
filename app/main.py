from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .schemas import AssessRequest, AssessResponse, Metric
from .orchestrator import Orchestrator

app = FastAPI(title="WASP Detector Green Agent")

orch = Orchestrator()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/assess", response_model=AssessResponse)
async def assess(req: AssessRequest):
    asr_i, asr_e, util, scenarios = orch.run_assessment(req.purple, req.wasp)

    metrics = [
        Metric(name="asr_intermediate", value=asr_i),
        Metric(name="asr_end_to_end", value=asr_e),
        Metric(name="utility", value=util),
    ]
    return AssessResponse(metrics=metrics, scenarios=scenarios)

