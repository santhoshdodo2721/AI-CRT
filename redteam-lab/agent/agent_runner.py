#!/usr/bin/env python3
import requests
import time
import subprocess
import json

SERVER = "http://localhost:8000"
MODULES_PATH = "/home/dodo/CRT/redteam-lab/modules"

def get_task():
    try:
        r = requests.get(f"{SERVER}/api/lab/next", timeout=5)
        if "id" in r.json():
            return r.json()
    except:
        pass
    return None

def submit_result(task_id, result):
    try:
        requests.post(f"{SERVER}/api/lab/{task_id}/submit", json={"result": result}, timeout=5)
    except:
        pass

def execute_module(task):
    module = task["module"]
    target = task["target"]
    print(f"[+] Executing {module} on {target}")
    
    module_file = f"{MODULES_PATH}/{module.replace('.', '/')}.py"
    cmd = ["python3", module_file, target]
    
    if "ports" in task:
        cmd.append(task["ports"])
        
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        out = result.stdout
        start = out.find("{")
        end = out.rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(out[start:end])
        return {"error": "No JSON", "raw": out[:200]}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("[*] Agent started. Listening for lab tasks...")
    while True:
        task = get_task()
        if task:
            print(f"\n[!] Task #{task['id']}: {task['module']} -> {task['target']}")
            result = execute_module(task)
            submit_result(task["id"], result)
            print(f"[+] Task #{task['id']} submitted.")
        else:
            print(".", end="", flush=True)
        time.sleep(3)
