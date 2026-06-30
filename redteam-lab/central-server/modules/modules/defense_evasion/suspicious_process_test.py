#!/usr/bin/env python3
import subprocess, json
cmd = "sleep 1 & echo $!"
out = subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
print(json.dumps({"technique_id":"T1036.004","technique_name":"Masquerading: Task or Service","risk_level":"Low","summary":"Process masquerading simulation executed","details":{"fake_name":"kworker/redteam_safe_test","action":"Simulated fork executed","pid":out}}, indent=2))