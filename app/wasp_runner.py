import subprocess
import json
from typing import List, Dict, Any
from .schemas import WaspConfig, ScenarioResult

class WaspRunner:
    def __init__(self, base_dir: str = "/app/wasp"):
        self.base_dir = base_dir

    def run_wasp(self, cfg: WaspConfig, purple_endpoint: str) -> List[ScenarioResult]:
        """
        Calls WASP's run.py with appropriate flags.
        For v1, assume we have a custom config that uses the purple agent as backend.
        """
        cmd = [
            "python",
            "webarena_prompt_injections/run.py",
            "--result_dir", "results",
            "--agent_endpoint", purple_endpoint,
        ]
        # Select subsets of tasks based on cfg.envs/modes (you’d wire this into WASP config files)
        # For simplicity here, run full benchmark.
        proc = subprocess.run(
            cmd,
            cwd=self.base_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        # Assume WASP writes a JSON summary file to results/summary.json
        summary_path = f"{self.base_dir}/results/summary.json"
        with open(summary_path, "r", encoding="utf-8") as f:
             Dict[str, Any] = json.load(f)

        scenarios: List[ScenarioResult] = []
        for s in data["scenarios"]:
            scenarios.append(
                ScenarioResult(
                    scenario_id=s["id"],
                    asr_intermediate=s["asr_intermediate"],
                    asr_end_to_end=s["asr_end_to_end"],
                    utility=s["utility"],
                    metadata={k: v for k, v in s.items() if k not in {"id", "asr_intermediate", "asr_end_to_end", "utility"}},
                )
            )
        return scenarios

