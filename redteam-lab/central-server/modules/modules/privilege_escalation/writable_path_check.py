#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("find /etc /usr/bin /usr/sbin -writable -type f 2>/dev/null | head -10", shell=True, capture_output=True, text=True).stdout.strip()
paths = [p for p in out.splitlines() if p]
print(json.dumps({"technique_id":"T1574.006","technique_name":"Hijack Execution Flow: LD_PRELOAD","risk_level":"High" if paths else "Low","summary":f"Found {len(paths)} writable privileged paths","details":[{"paths":paths}]}, indent=2))