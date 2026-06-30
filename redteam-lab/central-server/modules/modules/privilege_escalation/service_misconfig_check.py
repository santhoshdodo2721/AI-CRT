#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("systemctl list-units --type=service --state=running 2>/dev/null | head -10", shell=True, capture_output=True, text=True).stdout.strip()
services = [s.split()[0] for s in out.splitlines() if s]
print(json.dumps({"technique_id":"T1543.003","technique_name":"Linux Daemon Misconfig","risk_level":"Low","summary":f"Enumerated {len(services)} running services","details":{"running_services":services}}, indent=2))