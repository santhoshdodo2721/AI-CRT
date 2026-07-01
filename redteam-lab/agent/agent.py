#!/usr/bin/env python3
import subprocess
import sys
import time
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [AGENT] %(message)s")
logger = logging.getLogger("agent.main")

AGENT_DIR = Path(__file__).parent

def run_script(script_name):
    script_path = AGENT_DIR / script_name
    return subprocess.Popen([sys.executable, str(script_path)])

def main():
    logger.info("Initializing Agent (Phase 2 Architecture)...")
    
    # 1. Register
    logger.info(f"Running {AGENT_DIR}/register.py")
    reg_proc = subprocess.run([sys.executable, str(AGENT_DIR / "register.py")])
    if reg_proc.returncode != 0:
        logger.error("Registration failed. Exiting.")
        sys.exit(1)
        
    # 2. Start heartbeat in background
    logger.info("Starting heartbeat daemon...")
    hb_proc = run_script("heartbeat.py")
    
    # 3. Start task runner in foreground (or block here)
    logger.info("Starting task runner...")
    tr_proc = run_script("task_runner.py")
    
    try:
        # Wait indefinitely for task_runner
        tr_proc.wait()
    except KeyboardInterrupt:
        logger.info("Agent shutting down...")
    finally:
        hb_proc.terminate()
        tr_proc.terminate()

if __name__ == "__main__":
    main()
