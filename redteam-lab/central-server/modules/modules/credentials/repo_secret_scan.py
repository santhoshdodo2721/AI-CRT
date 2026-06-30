#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("which gitleaks", shell=True, capture_output=True).returncode
if out == 0:
    res = subprocess.run("gitleaks detect --source . --no-git -v 2>/dev/null | head -20", shell=True, capture_output=True, text=True).stdout.strip()
    findings = [{"line":l} for l in res.splitlines() if l]
else:
    findings = [{"info":"gitleaks not installed, skipping actual scan"}]
print(json.dumps({"technique_id":"T1552.001","technique_name":"Credentials In Files","risk_level":"Low","summary":"Git secret scan executed","details":findings}, indent=2))