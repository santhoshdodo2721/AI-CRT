#!/usr/bin/env python3
import socket, json, sys
target = sys.argv[1] if len(sys.argv)>1 else "localhost"
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
res = sock.connect_ex((target, 3389))
sock.close()
open_port = res == 0
print(json.dumps({"technique_id":"T1021.001","technique_name":"Remote Desktop Protocol","risk_level":"High" if open_port else "Low","summary":f"RDP (3389) is {'OPEN' if open_port else 'CLOSED/FILTERED'}","details":[{"port":3389,"state":"open" if open_port else "closed"}]}, indent=2))