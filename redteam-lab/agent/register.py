#!/usr/bin/env python3
import sys
import os
import yaml
import requests
import logging
from pathlib import Path

# Add the agent directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inventory import get_system_inventory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [REGISTER] %(message)s")
logger = logging.getLogger("agent.register")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
AGENT_ID_PATH = Path(__file__).parent / ".agent_id"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        logger.error(f"Config file not found: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)

def register():
    cfg = load_config()
    server_url = cfg.get("server_url", "http://localhost:8000").rstrip("/")
    
    logger.info("Gathering system inventory...")
    inventory = get_system_inventory()
    
    payload = {
        "name": cfg.get("agent_name", inventory["hostname"]),
        "hostname": inventory["hostname"],
        "ip_address": inventory["ip_address"],
        "os_info": inventory["os_info"],
    }
    
    logger.info(f"Registering with central server at {server_url}/api/agents/register ...")
    try:
        r = requests.post(f"{server_url}/api/agents/register", json=payload, timeout=30)
        r.raise_for_status()
        resp = r.json()
        
        if "agent_id" in resp:
            agent_id = resp["agent_id"]
            logger.info(f"Successfully registered. Agent ID: {agent_id} (Status: {resp.get('status')})")
            
            # Save the agent_id to a file for other components to read
            with open(AGENT_ID_PATH, "w") as f:
                f.write(agent_id)
            logger.info(f"Saved agent_id to {AGENT_ID_PATH}")
            return agent_id
        else:
            logger.error(f"Registration failed, invalid response: {resp}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to register with central server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    register()
