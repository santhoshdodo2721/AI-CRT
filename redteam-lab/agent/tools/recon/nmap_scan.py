#!/usr/bin/env python3
import subprocess
import json
import xml.etree.ElementTree as ET
import sys

def run_scan(target: str, ports: str = "1-10000") -> dict:
    sys.stderr.write(f"[*] Starting Nmap scan on {target} (ports: {ports})\n")
    
    # Run nmap and output as XML to stdout
    cmd = ["nmap", "-p", ports, "-T4", "-sV", "-oX", "-", target]
    
    try:
        sys.stderr.write(f"[DEBUG] Executing: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"error": "Nmap scan timed out"}
    except FileNotFoundError:
        return {"error": "Nmap is not installed or not in PATH"}

    if result.returncode != 0 and not result.stdout:
        return {"error": f"Nmap failed: {result.stderr}"}

    ports_found = []
    
    try:
        # Parse the Nmap XML output
        root = ET.fromstring(result.stdout)
        
        for host in root.findall('host'):
            for ports_node in host.findall('ports'):
                for port_node in ports_node.findall('port'):
                    state_node = port_node.find('state')
                    if state_node is not None and state_node.get('state') == 'open':
                        port_id = port_node.get('portid')
                        protocol = port_node.get('protocol')
                        
                        service_name = "unknown"
                        service_node = port_node.find('service')
                        if service_node is not None:
                            service_name = service_node.get('name', 'unknown')
                            
                        ports_found.append({
                            "port": port_id,
                            "protocol": protocol,
                            "state": "open",
                            "service": service_name
                        })
    except ET.ParseError as e:
        return {"error": f"Failed to parse Nmap XML: {e}", "raw": result.stdout[:200]}

    sys.stderr.write(f"[+] Scan complete. Found {len(ports_found)} open ports.\n")
    
    return {
        "target": target,
        "technique_id": "T1046",
        "open_ports": ports_found
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    ports = sys.argv[2] if len(sys.argv) > 2 else "1-10000"
    
    result = run_scan(target, ports)
    # The agent runner looks for the JSON block in stdout
    print(json.dumps(result, indent=2))
