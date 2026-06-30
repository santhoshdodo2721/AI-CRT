#!/usr/bin/env python3
import subprocess, json, time
marker = "redteam_lab_persist_cron_safe"
subprocess.run(f"(crontab -l 2>/dev/null; echo '* * * * * echo {marker}') | crontab -", shell=True, capture_output=True)
time.sleep(1)
verify = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True).stdout
success = marker in verify
clean = "\n".join(l for l in verify.splitlines() if marker not in l)
subprocess.run("crontab -", shell=True, input=clean, capture_output=True, text=True)
print(json.dumps({"technique_id":"T1053.003","technique_name":"Scheduled Task/Job: Cron","risk_level":"Medium" if success else "Low","summary":"Cron persistence simulated and cleaned","details":[{"installed":success,"cleaned_up":True}]}, indent=2))