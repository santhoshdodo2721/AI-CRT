#!/usr/bin/env python3
import socket
import json
import sys

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Validating SMB Reachability (T1021.002) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        # Check if SMB port 445 is listening
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            result = sock.connect_ex((target, 445))
            
            if result == 0:
                sys.stderr.write("[+] SMB Port 445 is open and reachable.\n")
                results.append({
                    "port": 445,
                    "service": "SMB",
                    "reachable": True
                })
                
                vulns.append({
                    "title": "Reachable SMB Service",
                    "description": "SMB (port 445) is accessible. Attackers commonly use SMB for lateral movement via Windows Admin Shares or vulnerabilities like EternalBlue.",
                    "severity": "medium",
                    "mitre_id": "T1021.002"
                })
            else:
                sys.stderr.write("[-] SMB Port 445 is closed or filtered.\n")
                results.append({
                    "port": 445,
                    "service": "SMB",
                    "reachable": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR checking SMB: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1021.002",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
