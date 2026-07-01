#!/usr/bin/env python3
import socket
import json
import sys

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Validating RDP Reachability (T1021.001) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        # Check if RDP port 3389 is listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            result = sock.connect_ex((target, 3389))
            
            if result == 0:
                sys.stderr.write("[+] RDP Port 3389 is open and reachable.\n")
                results.append({
                    "port": 3389,
                    "service": "RDP",
                    "reachable": True
                })
                
                vulns.append({
                    "title": "Reachable RDP Service",
                    "description": "Remote Desktop Protocol (port 3389) is accessible. RDP is frequently targeted for lateral movement and ransomware deployment using stolen credentials.",
                    "severity": "medium",
                    "mitre_id": "T1021.001"
                })
            else:
                sys.stderr.write("[-] RDP Port 3389 is closed or filtered.\n")
                results.append({
                    "port": 3389,
                    "service": "RDP",
                    "reachable": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR checking RDP: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1021.001",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
