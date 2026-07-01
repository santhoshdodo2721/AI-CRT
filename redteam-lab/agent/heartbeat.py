#!/usr/bin/env python3
import time
import requests
import logging
import yaml
import sys
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [HEARTBEAT] %(message)s")
logger = logging.getLogger("agent.heartbeat")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
AGENT_ID_PATH = Path(__file__).parent / ".agent_id"

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

def run_heartbeat_loop():
    cfg = load_config()
    server_url = cfg.get("server_url", "http://localhost:8000").rstrip("/")
    interval = cfg.get("heartbeat_interval", 30)
    agent_id = get_agent_id()
    
    logger.info(f"Starting heartbeat loop for agent {agent_id} (Interval: {interval}s)")
    
    # Optional status file that task_runner can update
    status_path = Path(__file__).parent / ".status"
    
    while True:
        status = "idle"
        if status_path.exists():
            with open(status_path) as f:
                status = f.read().strip()
                
        try:
            r = requests.post(
                f"{server_url}/api/agents/heartbeat",
                json={"agent_id": agent_id, "status": status},
                timeout=10
            )
            r.raise_for_status()
            logger.debug(f"Heartbeat sent (Status: {status})")
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            
        time.sleep(interval)

if __name__ == "__main__":
    run_heartbeat_loop()
