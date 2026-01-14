import docker
from typing import Tuple
from .schemas import PurpleAgentConfig, WaspConfig, ScenarioResult
from .wasp_runner import WaspRunner

class Orchestrator:
    def __init__(self):
        self.client = docker.from_env()
        self.wasp_runner = WaspRunner()

    def start_purple(self, cfg: PurpleAgentConfig) -> Tuple[str, docker.models.containers.Container]:
        """
        Start purple agent container in a shared network so WASP can call it.
        Assume purple exposes HTTP on 9000 in-container.
        """
        container = self.client.containers.run(
            cfg.image,
            command=cfg.command,
            entrypoint=cfg.entrypoint,
            environment=cfg.env,
            detach=True,
            network="agentbeats-net",  # created by compose/scenario
            name=None,
        )
        # Endpoint reachable from WASP / green agent
        endpoint = "http://purple-agent:9000"
        return endpoint, container

    def stop_container(self, container):
        try:
            container.stop(timeout=10)
        except Exception:
            pass
        try:
            container.remove(force=True)
        except Exception:
            pass

    def run_assessment(self, purple_cfg: PurpleAgentConfig, wasp_cfg: WaspConfig) -> Tuple[float, float, float, list[ScenarioResult]]:
        endpoint, cont = self.start_purple(purple_cfg)
        try:
            scenarios = self.wasp_runner.run_wasp(wasp_cfg, purple_endpoint=endpoint)
            # aggregate metrics
            if not scenarios:
                return 0.0, 0.0, 0.0, []

            asr_i = sum(s.asr_intermediate for s in scenarios) / len(scenarios)
            asr_e = sum(s.asr_end_to_end for s in scenarios) / len(scenarios)
            util = sum(s.utility for s in scenarios) / len(scenarios)
            return asr_i, asr_e, util, scenarios
        finally:
            self.stop_container(cont)

