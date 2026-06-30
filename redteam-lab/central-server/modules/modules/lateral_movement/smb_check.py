#!/usr/bin/env python3
import subprocess, json, sys
target = sys.argv[1] if len(sys.argv)>1 else "localhost"
out = subprocess.run(f"smbclient -L //{target} -N 2>&1 | head -20", shell=True, capture_output=True, text=True).stdout
shares = [l.split()[1] for l in out.splitlines() if "Disk" in l or "Print" in l]
print(json.dumps({"technique_id":"T1021.002","technique_name":"SMB/Windows Admin Shares","risk_level":"High" if shares else "Low","summary":f"Found {len(shares)} accessible SMB shares","details":{"shares":shares,"raw_output":out[:500]}}, indent=2))