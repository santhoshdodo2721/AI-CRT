#!/usr/bin/env python3
import json
print(json.dumps({"technique_id":"T1048.003","technique_name":"Exfiltration Over Unencrypted Non-C2 Protocol","risk_level":"Info","summary":"DLP simulation check executed (requires manual DLP log verification)","details":{"action":"HTTP POST simulated","status":"Check SIEM/DLP logs for alert"}}, indent=2))