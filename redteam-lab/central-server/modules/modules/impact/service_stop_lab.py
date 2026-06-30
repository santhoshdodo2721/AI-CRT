#!/usr/bin/env python3
import subprocess, json
svc = "cron"
out = subprocess.run(f"systemctl stop {svc} 2>&1 && systemctl start {svc} 2>&1", shell=True, capture_output=True, text=True)
print(json.dumps({"technique_id":"T1489","technique_name":"Service Stop","risk_level":"Medium","summary":f"Service stop/start test on '{svc}' completed","details":{"service":svc,"output":out.stdout[:200]}}, indent=2))