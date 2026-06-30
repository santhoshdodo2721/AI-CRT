#!/usr/bin/env python3
import json
print(json.dumps({"technique_id":"T1053.005","technique_name":"Scheduled Task","risk_level":"Info","summary":"Windows Scheduled Task test skipped (Linux target)","details":[{"os":"Linux","action":"Skipped"}]}, indent=2))