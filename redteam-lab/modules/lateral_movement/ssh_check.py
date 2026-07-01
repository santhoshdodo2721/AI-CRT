#!/usr/bin/env python3
import socket
import json
import sys

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Validating SSH Reachability and Banner (T1021.004) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        # Check if SSH port 22 is listening and grab banner
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            result = sock.connect_ex((target, 22))
            
            if result == 0:
                sys.stderr.write("[+] SSH Port 22 is open.\n")
                
                # Attempt to grab the banner
                banner = "Unknown"
                try:
                    sock.settimeout(3.0)
                    banner_bytes = sock.recv(1024)
                    banner = banner_bytes.decode('utf-8').strip()
                    sys.stderr.write(f"[+] SSH Banner: {banner}\n")
                except Exception as b_err:
                    sys.stderr.write(f"[DEBUG] Could not grab SSH banner: {b_err}\n")
                    
                results.append({
                    "port": 22,
                    "service": "SSH",
                    "reachable": True,
                    "banner": banner
                })
                
                vulns.append({
                    "title": "Reachable SSH Service",
                    "description": f"SSH (port 22) is accessible. This service can be brute-forced or used for lateral movement if credentials/keys are compromised.\nBanner: {banner}",
                    "severity": "medium",
                    "mitre_id": "T1021.004"
                })
            else:
                sys.stderr.write("[-] SSH Port 22 is closed or filtered.\n")
                results.append({
                    "port": 22,
                    "service": "SSH",
                    "reachable": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR checking SSH: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1021.004",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
