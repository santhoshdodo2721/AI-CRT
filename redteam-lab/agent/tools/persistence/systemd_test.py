#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import time

def run_persistence(target: str) -> dict:
    sys.stderr.write(f"[*] Testing Persistence (T1543.002) via Systemd on {target}...\n")
    
    results = []
    vulns = []
    success = False
    
    service_dir = os.path.expanduser("~/.config/systemd/user")
    service_file = os.path.join(service_dir, "sim_persistence.service")
    
    service_content = """[Unit]
Description=Simulated Persistence Service

[Service]
ExecStart=/bin/echo "Persistence simulation running"

[Install]
WantedBy=default.target
"""

    try:
        # 1. Create directory if not exists
        os.makedirs(service_dir, exist_ok=True)
        
        # 2. Write service file
        sys.stderr.write(f"[DEBUG] Writing mock service to {service_file}...\n")
        with open(service_file, "w") as f:
            f.write(service_content)
            
        # 3. Verify it exists
        if os.path.exists(service_file):
            success = True
            sys.stderr.write("[+] Successfully dropped simulated systemd service.\n")
            
            results.append({
                "action": "create_systemd_service",
                "path": service_file,
                "success": True
            })
            
            vulns.append({
                "title": "Systemd Service Persistence Simulation",
                "description": f"Successfully simulated persistence by dropping a user-level systemd service file at {service_file}.",
                "severity": "medium",
                "mitre_id": "T1543.002"
            })
        else:
            sys.stderr.write("[-] Failed to create service file.\n")
            results.append({"action": "create_systemd_service", "success": False})

    except Exception as e:
        results.append({"action": "systemd_persistence", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during systemd test: {e}\n")
    finally:
        # 4. CLEANUP: Remove the file
        if os.path.exists(service_file):
            sys.stderr.write(f"[DEBUG] Cleaning up {service_file}...\n")
            os.remove(service_file)
            sys.stderr.write("[+] Cleanup successful.\n")
            
    return {
        "target": target if target else "local",
        "technique_id": "T1543.002",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_persistence(target), indent=2))
