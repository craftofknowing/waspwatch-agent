from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.webhook import router as webhook_router
from app.schemes import AssessResponse

app = FastAPI(title="WaspWatch 🐝 AgentBeats Green Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])

@app.get("/health")
async def health():
    return {"status": "healthy", "metrics": ["asr_intermediate", "asr_end_to_end", "utility"]}

@app.get("/")
async def root():
    return {"WaspWatch": "AgentBeats Green Agent v1.0.0 🏆"}

