#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("sudo -n -l 2>&1", shell=True, capture_output=True, text=True).stdout
misconfig = any(k in out.lower() for k in ["may run", "(root)", "(all)"])
print(json.dumps({"technique_id":"T1548.003","technique_name":"Sudo and Sudo Caching","risk_level":"High" if misconfig else "Low","summary":"Sudo misconfiguration detected" if misconfig else "No sudo misconfig found","details":[{"sudo_output":out, "vulnerable":misconfig}]}, indent=2))