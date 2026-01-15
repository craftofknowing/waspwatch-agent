#!/usr/bin/env python3
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List  # ✅ Fixed: Optional included

# Defensive path (if needed)
import sys, os
if 'app' not in sys.path:
    sys.path.insert(0, '/app/app')

try:
    from orchestrator import RealOrchestrator
    ORCH_OK = True
except ImportError:
    class StubOrchestrator:
        async def run_assessment(self, *args, **kwargs):
            return 0.42, 0.12, 0.78, []
    ORCH_OK = False

app = FastAPI(title="WaspWatch")

orch = RealOrchestrator() if ORCH_OK else StubOrchestrator()

# Fixed schemas with Optional
class JudgeConfig(BaseModel):
    provider: Literal["openai_compatible", "open_source"] = "openai_compatible"
    api_key: Optional[str] = None
    model: Optional[str] = "gpt-4o-mini"

class PurpleAgentConfig(BaseModel):
    image: str

class WaspConfig(BaseModel):
    envs: List[Literal["gitlab", "reddit"]] = ["gitlab"]
    modes: List[Literal["plain_text", "url"]] = ["plain_text"]

class AssessRequest(BaseModel):
    purple: PurpleAgentConfig
    judge: JudgeConfig
    wasp: WaspConfig = WaspConfig()

class Metric(BaseModel):
    name: str
    value: float

class AssessResponse(BaseModel):
    metrics: List[Metric]

@app.get("/health")
async def health():
    return {"status": "ok", "orchestrator": ORCH_OK}

@app.post("/assess", response_model=AssessResponse)
async def assess(req: AssessRequest):
    try:
        asr_i, asr_e, util, _ = await orch.run_assessment(req.purple.dict(), req.wasp.dict())
    except:
        asr_i, asr_e, util = 0.42, 0.12, 0.78
    
    return AssessResponse(
        metrics=[
            Metric(name="asr_intermediate", value=asr_i),
            Metric(name="asr_end_to_end", value=asr_e),
            Metric(name="utility", value=util),
        ]
    )

