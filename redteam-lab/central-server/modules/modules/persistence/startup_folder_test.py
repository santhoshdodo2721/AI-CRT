#!/usr/bin/env python3
import json
print(json.dumps({"technique_id":"T1547.001","technique_name":"Startup Folder","risk_level":"Info","summary":"Windows Startup Folder test skipped (Linux target)","details":[{"os":"Linux","action":"Skipped"}]}, indent=2))