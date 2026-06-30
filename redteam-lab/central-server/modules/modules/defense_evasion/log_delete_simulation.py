#!/usr/bin/env python3
import os, json
logs = ["/var/log/syslog", "/var/log/auth.log"]
results = []
for log in logs:
    exists = os.path.exists(log)
    writable = os.access(log, os.W_OK) if exists else False
    results.append({"file":log,"exists":exists,"writable":writable,"action":"Checked permissions only"})
print(json.dumps({"technique_id":"T1070.002","technique_name":"Clear Linux or Mac System Logs","risk_level":"High" if any(r['writable'] for r in results) else "Low","summary":"Log deletion permission check completed safely","details":results}, indent=2))