#!/usr/bin/env python3
import subprocess, json
out = subprocess.run("ps aux | grep -E 'edefend|crowdstrike|sentinel|ossec|snort|suricata' | grep -v grep", shell=True, capture_output=True, text=True).stdout.strip()
tools = [l.split()[10] for l in out.splitlines() if l] if out else []
print(json.dumps({"technique_id":"T1082","technique_name":"System Information Discovery","risk_level":"Medium" if tools else "Low","summary":f"Security tools detected: {len(tools)}","details":{"detected_tools":tools,"action":"Checked for common EDR/AV processes"}}, indent=2))