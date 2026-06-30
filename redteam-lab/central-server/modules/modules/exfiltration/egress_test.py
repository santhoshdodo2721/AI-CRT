#!/usr/bin/env python3
import socket, json
ports = [80, 443, 53, 8080, 8888, 9999]
results = []
for p in ports:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    res = s.connect_ex(("8.8.8.8", p))
    results.append({"port":p,"egress_allowed": res==0})
    s.close()
print(json.dumps({"technique_id":"T1041","technique_name":"Exfiltration Over C2 Channel","risk_level":"High" if any(r['egress_allowed'] for r in results if r['port'] not in [80,443,53]) else "Medium","summary":"Egress firewall rules tested","details":results}, indent=2))