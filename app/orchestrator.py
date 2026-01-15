#!/usr/bin/env python3
"""
WaspWatch Orchestrator: Production WASP Detection Engine
Full Docker orchestration + WASP benchmark runner for AgentBeats green agent
"""

import docker
import subprocess
import json
import tempfile
import os
import time
import shutil
from typing import Tuple, List, Dict, Any
from docker.errors import NotFound
import asyncio

class RealOrchestrator:
    def __init__(self, wasp_base_dir: str = "/app/wasp"):
        """Initialize with Docker client and fallback handling."""
        self.docker_available = False
        self.docker_client = None
        
        # Initialize Docker with fallback
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Test connection
            self.docker_available = True
            print("✅ Docker orchestrator ready")
        except Exception as e:
            print(f"⚠️  Docker unavailable ({e}). Using fallback mode.")
            self.docker_client = None
        
        self.wasp_base_dir = wasp_base_dir
        self.wasp_runner = os.path.join(wasp_base_dir, "webarena_prompt_injections", "run.py")
        self._ensure_network()
    
    def _ensure_network(self):
        """Create shared wasp-net for purple agents + web envs."""
        if not self.docker_available:
            return
        
        try:
            self.docker_client.networks.get("wasp-net")
            print("✅ wasp-net exists")
        except NotFound:
            self.docker_client.networks.create("wasp-net", driver="bridge")
            print("✅ Created wasp-net")
    
    def _start_web_envs(self) -> Dict[str, str]:
        """Configure WASP web environments."""
        envs = {
            "REDDIT": "reddit:9999",
            "GITLAB": "gitlab:8023",
            "DOCKER_HOST": "unix:///var/run/docker.sock"
        }
        os.environ.update(envs)
        return envs
    
    def _start_purple_agent(self, purple_cfg: Dict[str, Any]) -> Tuple[str, str]:
        """Start purple agent container or return mock."""
        if not self.docker_available:
            print("🔄 Using mock purple agent (Docker unavailable)")
            return "mock://purple-agent:9000", "mock-container-id"
        
        try:
            container = self.docker_client.containers.run(
                image=purple_cfg["image"],
                detach=True,
                network="wasp-net",
                environment=purple_cfg.get("env", {}),
                ports={"9000/tcp": None},  # Standard agent API port
                name="purple-agent",
                remove=True,
                mem_limit="2g",
                cpus=2.0,
            )
            print(f"✅ Started purple agent: {container.id}")
            return f"http://purple-agent:9000", container.id
        except Exception as e:
            print(f"❌ Failed to start purple agent: {e}")
            return "error://purple-agent:9000", "error-container"
    
    def _generate_wasp_config(self, env: str, mode: str) -> str:
        """Generate WASP config file."""
        config_dir = os.path.join(self.wasp_base_dir, "webarena_prompt_injections", "configs")
        config_name = f"{env}_{mode}.json"
        config_path = os.path.join(config_dir, config_name)
        
        if os.path.exists(config_path):
            return config_path
        
        # Generate minimal config
        config = {
            "environment": env,
            "injection_mode": mode,
            "agent_model": "gpt-4o",
            "max_steps": 50,
            "timeout": 300
        }
        
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"📝 Generated config: {config_path}")
        return config_path
    
    def _run_wasp_scenario(self, config_path: str, model: str, output_dir: str) -> Dict[str, Any]:
        """Execute single WASP benchmark scenario."""
        if not os.path.exists(config_path):
            return {"status": "failed", "error": f"Config missing: {config_path}"}
        
        cmd = [
            "python", self.wasp_runner,
            "--config", config_path,
            "--model", model,
            "--output-dir", output_dir,
            "--output-format", "json",
            "--max-steps", "50",
            "--timeout", "300"
        ]
        
        print(f"🏃 Running WASP: {' '.join(cmd[-5:])}")
        
        result = subprocess.run(
            cmd, 
            cwd=self.wasp_base_dir,
            capture_output=True, 
            text=True, 
            timeout=330,  # 5.5min buffer
            env={**os.environ, "PYTHONPATH": f"/app:/app/app:{os.environ.get('PYTHONPATH', '')}"}
        )
        
        # Parse results
        results = {
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
        
        # Try to load summary JSON
        summary_path = os.path.join(output_dir, "summary.json")
        if os.path.exists(summary_path):
            try:
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                    results.update(summary)
                    print(f"📊 WASP results: ASR-I={summary.get('asr_intermediate', 0):.2f}, ASR-E={summary.get('asr_end_to_end', 0):.2f}")
            except json.JSONDecodeError:
                results["summary_parse_error"] = True
        
        return results
    
    async def run_assessment(self, purple_cfg: Dict[str, Any], wasp_cfg: Dict[str, Any]) -> Tuple[float, float, float, List[Dict]]:
        """Execute full WASP assessment pipeline."""
        print("🚀 Starting WaspWatch assessment...")
        
        scenarios = []
        totals = {"asr_i": 0.0, "asr_e": 0.0, "util": 0.0, "count": 0}
        
        # Configure environments
        self._start_web_envs()
        
        temp_dir = tempfile.mkdtemp(prefix="wasp-assess-")
        container_id = None
        
        try:
            # Start purple agent
            purple_endpoint, container_id = self._start_purple_agent(purple_cfg)
            print(f"🟣 Purple agent: {purple_endpoint}")
            
            # Run configured scenarios
            model = purple_cfg.get("judge", {}).get("model", "gpt-4o")
            
            for env in wasp_cfg.get("envs", ["gitlab"]):
                for mode in wasp_cfg.get("modes", ["plain_text"]):
                    scenario_id = f"{env}_{mode}"
                    config_path = self._generate_wasp_config(env, mode)
                    
                    print(f"🔬 Running scenario: {scenario_id}")
                    
                    scenario_results = self._run_wasp_scenario(
                        config_path, model, temp_dir
                    )
                    
                    # Extract metrics (with fallbacks)
                    asr_i = scenario_results.get("asr_intermediate", 0.0)
                    asr_e = scenario_results.get("asr_end_to_end", 0.0)
                    util = scenario_results.get("utility", 0.0)
                    
                    totals["asr_i"] += asr_i
                    totals["asr_e"] += asr_e
                    totals["util"] += util
                    totals["count"] += 1
                    
                    scenarios.append({
                        "scenario_id": scenario_id,
                        "asr_intermediate": float(asr_i),
                        "asr_end_to_end": float(asr_e),
                        "utility": float(util),
                        "status": scenario_results["status"],
                        "raw_results": {k: v for k, v in scenario_results.items() if k not in ["stdout", "stderr"]}
                    })
            
            print(f"📈 Assessment complete: {totals['count']} scenarios")
            
        except Exception as e:
            print(f"❌ Assessment failed: {e}")
            scenarios = [{"scenario_id": "error", "asr_intermediate": 0.0, "asr_end_to_end": 0.0, "utility": 0.0}]
        
        finally:
            # Cleanup
            if container_id and self.docker_available:
                try:
                    self.docker_client.containers.get(container_id).stop(timeout=10)
                    print("🧹 Purple agent stopped")
                except:
                    pass
            
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Compute final metrics
        count = max(totals["count"], 1)
        return (
            totals["asr_i"] / count,
            totals["asr_e"] / count,
            totals["util"] / count,
            scenarios
        )

