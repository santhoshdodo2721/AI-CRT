#!/usr/bin/env python3
import time
import requests
import logging
import yaml
import sys
import os
import subprocess
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] [TASK_RUNNER] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "logs" / "agent.log")
    ]
)
logger = logging.getLogger("agent.task_runner")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
AGENT_ID_PATH = Path(__file__).parent / ".agent_id"
STATUS_PATH = Path(__file__).parent / ".status"
TOOLS_PATH = Path(__file__).parent / "tools"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        logger.error(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def get_agent_id() -> str:
    if not AGENT_ID_PATH.exists():
        logger.error(f"Agent ID file not found. Please run register.py first.")
        sys.exit(1)
    with open(AGENT_ID_PATH) as f:
        return f.read().strip()

def set_status(status: str):
    with open(STATUS_PATH, "w") as f:
        f.write(status)

def run_task_loop():
    cfg = load_config()
    server_url = cfg.get("server_url", "http://localhost:8000").rstrip("/")
    poll_interval = cfg.get("poll_interval", 10)
    allowed_modules = cfg.get("allowed_modules", [])
    agent_id = get_agent_id()
    
    logger.info(f"Starting task runner loop for agent {agent_id} (Poll interval: {poll_interval}s)")
    set_status("idle")
    
    while True:
        try:
            r = requests.get(f"{server_url}/api/agents/tasks/next/{agent_id}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                task = data.get("task")
                if task:
                    task_id = task["id"]
                    module = task["module"]
                    params = task.get("params", {})
                    
                    logger.info(f"Received task {task_id}: {module}")
                    set_status("running")
                    
                    if module not in allowed_modules:
                        logger.warning(f"Module {module} is NOT in allowed_modules. Rejecting.")
                        submit_result(server_url, task_id, agent_id, "failed", {"error": "Module not permitted by agent config"})
                        set_status("idle")
                        continue
                        
                    result = execute_module(module, params)
                    submit_result(server_url, task_id, agent_id, "completed", result)
                    set_status("idle")
        except requests.exceptions.RequestException as e:
            pass # Server might be down or unreachable, just continue polling
        except Exception as e:
            logger.error(f"Error in task runner loop: {e}")
            set_status("idle")
            
        time.sleep(poll_interval)

def execute_module(module: str, params: dict) -> dict:
    module_file = TOOLS_PATH / f"{module.replace('.', '/')}.py"
    if not module_file.exists():
        return {"error": f"Tool file not found: {module_file}"}
        
    target = params.get("target") or params.get("target_ip") or params.get("domain") or "127.0.0.1"
    cmd = ["python3", str(module_file), target]
    
    if "ports" in params:
        cmd.append(params["ports"])
        
    logger.info(f"Executing: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = res.stdout
        
        # Parse output for JSON block
        start = out.find("{")
        end = out.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(out[start:end])
        return {"error": "No JSON", "raw": out[:200], "stderr": res.stderr[:500]}
    except Exception as e:
        return {"error": str(e)}

def submit_result(server_url: str, task_id: str, agent_id: str, status: str, result: dict):
    logger.info(f"Submitting result for task {task_id} ({status})")
    try:
        r = requests.post(
            f"{server_url}/api/agents/tasks/result",
            json={"task_id": task_id, "agent_id": agent_id, "status": status, "result": result},
            timeout=10
        )
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to submit result for task {task_id}: {e}")

if __name__ == "__main__":
    run_task_loop()
