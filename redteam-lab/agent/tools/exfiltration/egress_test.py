#!/usr/bin/env python3
import socket
import json
import sys

def run_exfiltration(target: str) -> dict:
    sys.stderr.write(f"[*] Simulating Outbound Egress (T1041) on {target}...\n")
    
    results = []
    vulns = []
    allowed = []
    
    EGRESS_TARGETS = [
        {"host": "ifconfig.me",    "port": 80,  "proto": "http"},
        {"host": "ifconfig.me",    "port": 443, "proto": "https"},
        {"host": "1.1.1.1",        "port": 53,  "proto": "dns"},
        {"host": "github.com",     "port": 443, "proto": "https"},
        {"host": "portquiz.net",   "port": 8080, "proto": "http"},
    ]
    
    try:
        sys.stderr.write("[DEBUG] Testing common egress ports...\n")
        
        for tgt in EGRESS_TARGETS:
            host = tgt["host"]
            port = tgt["port"]
            proto = tgt["proto"]
            
            try:
                s = socket.create_connection((host, port), timeout=3)
                s.close()
                reachable = True
                allowed.append(f"{proto}://{host}:{port}")
                sys.stderr.write(f"[+] Outbound {proto.upper()} ({port}) allowed to {host}.\n")
            except Exception:
                reachable = False
                sys.stderr.write(f"[-] Outbound {proto.upper()} ({port}) blocked/failed to {host}.\n")
                
            results.append({
                "host": host,
                "port": port,
                "protocol": proto,
                "reachable": reachable
            })
            
        if allowed:
            vulns.append({
                "title": "Unrestricted Outbound Egress",
                "description": f"The host can freely establish outbound connections on common ports, which can be abused for C2 communication or data exfiltration.\nAllowed paths:\n" + "\n".join(allowed),
                "severity": "medium",
                "mitre_id": "T1041"
            })
        else:
            sys.stderr.write("[+] All tested egress ports appear to be blocked.\n")
            
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during egress test: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1041",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_exfiltration(target), indent=2))
