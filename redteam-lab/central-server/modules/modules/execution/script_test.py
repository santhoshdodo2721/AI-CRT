#!/usr/bin/env python3
import subprocess, json, tempfile, os
script = "echo \"Red Team Safe Script Execution Test\"; whoami; pwd"
with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
    f.write(script)
    sfile = f.name
os.chmod(sfile, 0o755)
out = subprocess.run(f"bash {sfile}", shell=True, capture_output=True, text=True).stdout.strip()
os.remove(sfile)
print(json.dumps({"technique_id":"T1059.004","technique_name":"Unix Shell Script","risk_level":"Info","summary":"Safe bash script executed successfully","details":[{"script_output":out}]}, indent=2))