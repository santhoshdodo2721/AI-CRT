#!/usr/bin/env python3
import socket
import sys
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# A small subset of critical ports for quick lab testing instead of scanning 65k ports
LATERAL_PORTS = {
    22: "SSH",
    135: "RPC",
    139: "NetBIOS",
    445: "SMB",
    3389: "RDP",
    5985: "WinRM",
    5986: "WinRM SSL"
}

def scan_port(ip: str, port: int, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                return (port, "open", LATERAL_PORTS.get(port, "unknown"))
            return (port, "closed", None)
    except socket.timeout:
        return (port, "filtered", None)
    except Exception as e:
        return (port, "error", str(e))

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Scanning {target} for lateral movement vectors (T1046)...\n")
    
    results = []
    vulns = []
    open_ports = []
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(scan_port, target, port): port for port in LATERAL_PORTS.keys()}
            
            for future in as_completed(futures):
                port, state, service = future.result()
                
                results.append({
                    "port": port,
                    "state": state,
                    "service": service
                })
                
                if state == "open":
                    open_ports.append(port)
                    sys.stderr.write(f"[+] Port {port}/tcp open ({service})\n")
                    
                    vulns.append({
                        "title": f"Exposed Lateral Movement Port: {port}",
                        "description": f"The target exposes port {port} ({service}), which is commonly used by attackers to pivot and move laterally across a network.",
                        "severity": "medium",
                        "mitre_id": "T1046"
                    })
                    
        if not open_ports:
            sys.stderr.write("[-] No lateral movement ports found open.\n")
            
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during network scan: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1046",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
