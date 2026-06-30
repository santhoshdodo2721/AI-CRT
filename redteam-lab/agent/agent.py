import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#!/usr/bin/env python3
"""
RedTeam Lab Agent
Runs on each target/pivot machine in the lab network.
Only executes modules explicitly assigned by the central server.
"""

import time
import socket
import platform
import logging
import importlib
import yaml
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("agent")

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


class Agent:
    def __init__(self):
        self.cfg     = load_config()
        self.server  = self.cfg["server_url"].rstrip("/")
        self.agent_id: str = ""

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _post(self, path: str, data: dict) -> dict:
        try:
            r = requests.post(f"{self.server}{path}", json=data, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"POST {path} failed: {e}")
            return {}

    def _get(self, path: str) -> dict:
        try:
            r = requests.get(f"{self.server}{path}", timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            log.error(f"GET {path} failed: {e}")
            return {}

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def register(self):
        log.info("Registering with central server …")
        resp = self._post("/api/agents/register", {
            "name":       self.cfg.get("agent_name", socket.gethostname()),
            "hostname":   socket.gethostname(),
            "ip_address": self._local_ip(),
            "os_info":    platform.platform(),
        })
        if "agent_id" in resp:
            self.agent_id = resp["agent_id"]
            log.info(f"Registered. Agent ID: {self.agent_id}")
        else:
            log.error(f"Registration failed: {resp}")

    def heartbeat(self):
        self._post("/api/agents/heartbeat", {"agent_id": self.agent_id, "status": "idle"})

    # ── Task execution ────────────────────────────────────────────────────────

    def poll_and_run(self):
        resp = self._get(f"/api/agents/tasks/next/{self.agent_id}")
        task = resp.get("task")
        if not task:
            return

        task_id = task["id"]
        module  = task["module"]    # e.g. "recon.nmap_scan"
        params  = task.get("params", {})

        log.info(f"Received task {task_id}: {module}")

        # Safety check: only run allowlisted modules
        allowed = set(self.cfg.get("allowed_modules", []))
        if module not in allowed:
            log.warning(f"Module {module} not in allowlist – skipping.")
            self._post("/api/agents/tasks/result", {
                "task_id":  task_id,
                "agent_id": self.agent_id,
                "status":   "failed",
                "result":   {"error": f"Module {module} not allowed on this agent."},
            })
            return

        result = self._run_module(module, params)
        self._post("/api/agents/tasks/result", {
            "task_id":  task_id,
            "agent_id": self.agent_id,
            "status":   "completed" if "error" not in result else "failed",
            "result":   result,
        })
        log.info(f"Task {task_id} submitted.")

    def _run_module(self, module_path: str, params: dict) -> dict:
        """Dynamically import and run a module from the modules/ directory."""
        try:
            mod = importlib.import_module(f"modules.{module_path.replace('.', '_')}")
            return mod.run(params)
        except ModuleNotFoundError:
            # Try dot-path directly
            try:
                parts = module_path.rsplit(".", 1)
                mod = importlib.import_module(f"modules.{parts[0]}.{parts[1]}")
                return mod.run(params)
            except Exception as e:
                return {"error": str(e)}
        except Exception as e:
            log.exception(f"Module {module_path} raised an exception")
            return {"error": str(e)}

    # ── Utilities ─────────────────────────────────────────────────────────────

    @staticmethod
    def _local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        self.register()
        if not self.agent_id:
            log.error("Could not obtain agent ID. Exiting.")
            return

        heartbeat_interval = self.cfg.get("heartbeat_interval", 30)
        poll_interval      = self.cfg.get("poll_interval", 10)
        tick               = 0

        while True:
            self.poll_and_run()
            tick += poll_interval
            if tick >= heartbeat_interval:
                self.heartbeat()
                tick = 0
            time.sleep(poll_interval)


if __name__ == "__main__":
    Agent().run()
