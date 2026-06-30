#!/usr/bin/env python3
import subprocess, json, time
subprocess.Popen("dd if=/dev/zero of=/dev/null & sleep 3 && kill $!", shell=True)
time.sleep(4)
print(json.dumps({"technique_id":"T1499.001","technique_name":"OS Exhaustion Flood","risk_level":"Medium","summary":"Brief 3-second CPU load test completed","details":{"duration_sec":3,"action":"Safe load generated and stopped"}}, indent=2))