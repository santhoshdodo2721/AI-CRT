#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("find /usr /bin /sbin -perm -4000 -type f 2>/dev/null | head -15", shell=True, capture_output=True, text=True).stdout.strip()
bins = [b for b in out.splitlines() if b]
print(json.dumps({"technique_id":"T1548.001","technique_name":"Setuid and Setgid","risk_level":"Medium" if bins else "Low","summary":f"Found {len(bins)} SUID binaries","details":[{"binaries":bins,"count":len(bins)}]}, indent=2))