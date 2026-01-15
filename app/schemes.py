from typing import Dict, Any
from pydantic import Field
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PurpleAgentConfig(BaseModel):
    image: str
    command: Optional[List[str]] = None
    env: Optional[Dict[str, str]] = None

class AssessmentResult(BaseModel):
    id: str
    asr_intermediate: float = Field(..., description="Hijack success rate")
    asr_end_to_end: float = Field(..., description="Full compromise rate")
    utility: float = Field(..., description="Benign task success")
    agent_type: str = "green"

class AssessResponse(BaseModel):
    results: List[AssessmentResult]
    meta: Dict[str, Any] = Field(default_factory=dict)  # ✅ FIXED!

