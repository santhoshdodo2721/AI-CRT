#!/usr/bin/env python3
import subprocess
import json
import xml.etree.ElementTree as ET
import sys

def run_scan(target: str, ports: str = "1-10000") -> dict:
    print(f"[*] Starting Nmap scan on {target} (ports: {ports})")
    cmd = ["nmap", "-sV", "-Pn", "-p", ports, "-oX", "-", target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        root = ET.fromstring(result.stdout)
        
        ports_found = []
        for host in root.findall("host"):
            for port in host.findall("ports/port"):
                port_id = port.get("portid")
                protocol = port.get("protocol")
                state = port.find("state").get("state") if port.find("state") is not None else "unknown"
                service = port.find("service").get("name", "unknown") if port.find("service") is not None else "unknown"
                
                if state == "open":
                    ports_found.append({
                        "port": port_id,
                        "protocol": protocol,
                        "state": state,
                        "service": service
                    })
        
        print(f"[+] Scan complete. Found {len(ports_found)} open ports.")
        return {
            "target": target,
            "technique_id": "T1046",
            "open_ports": ports_found,
            "raw_output": result.stdout
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    # Changed: defaults to 1-10000 now to catch things like 8000
    ports = sys.argv[2] if len(sys.argv) > 2 else "1-10000"
    print(json.dumps(run_scan(target, ports), indent=2))
