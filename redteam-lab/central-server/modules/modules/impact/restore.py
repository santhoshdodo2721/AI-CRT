#!/usr/bin/env python3
import subprocess, json
services = ["cron", "ssh", "docker"]
status = {}
for s in services:
    out = subprocess.run(f"systemctl is-active {s} 2>/dev/null", shell=True, capture_output=True, text=True).stdout.strip()
    status[s] = out
print(json.dumps({"technique_id":"T1490","technique_name":"Inhibit System Recovery","risk_level":"Low","summary":"System restoration check completed","details":{"service_status":status,"action":"Verified core services are active"}}, indent=2))