#!/usr/bin/env python3
import subprocess, json
endpoints = ["http://169.254.169.254/latest/meta-data/", "http://metadata.google.internal/"]
results = []
for ep in endpoints:
    out = subprocess.run(f"curl -s --connect-timeout 2 {ep}", shell=True, capture_output=True, text=True).stdout.strip()
    results.append({"url":ep,"accessible": len(out)>0 and "404" not in out})
print(json.dumps({"technique_id":"T1552.005","technique_name":"Cloud Instance Metadata API","risk_level":"Critical" if any(r['accessible'] for r in results) else "Low","summary":"Cloud metadata token check completed","details":results}, indent=2))