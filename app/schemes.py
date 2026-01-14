from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

class JudgeConfig(BaseModel):
    provider: Literal["openai_compatible", "open_source"]
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    engine_type: Optional[Literal["vllm", "ollama", "hf_endpoint", "local"]] = None
    endpoint_url: Optional[str] = None
    model_id: Optional[str] = None

class PurpleAgentConfig(BaseModel):
    image: str
    entrypoint: Optional[str] = None
    command: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)

class WaspConfig(BaseModel):
    envs: List[Literal["gitlab", "reddit"]] = ["gitlab", "reddit"]
    modes: List[Literal["plain_text", "url"]] = ["plain_text", "url"]
    max_tasks: Optional[int] = None

class AssessRequest(BaseModel):
    purple: PurpleAgentConfig
    judge: JudgeConfig
    wasp: WaspConfig = WaspConfig()

class Metric(BaseModel):
    name: str
    value: float

class ScenarioResult(BaseModel):
    scenario_id: str
    asr_intermediate: float
    asr_end_to_end: float
    utility: float
    meta Dict[str, Any] = Field(default_factory=dict)

class AssessResponse(BaseModel):
    metrics: List[Metric]
    scenarios: List[ScenarioResult]

