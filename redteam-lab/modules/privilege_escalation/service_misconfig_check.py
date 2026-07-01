#!/usr/bin/env python3
import subprocess
import json
import sys
import os

def run_privesc(target: str) -> dict:
    sys.stderr.write(f"[*] Checking for Systemd Service Misconfigurations (T1543.002) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        sys.stderr.write("[DEBUG] Searching for world-writable systemd services...\n")
        
        # Look for world-writable files in common systemd directories
        cmd = "find /etc/systemd/system /lib/systemd/system /usr/lib/systemd/system -type f -name '*.service' -perm -0002 2>/dev/null"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        writable_services = [s.strip() for s in r.stdout.splitlines() if s.strip()]
        
        results.append({
            "action": "find_writable_services",
            "services": writable_services
        })
        
        if writable_services:
            sys.stderr.write(f"[!] ALERT: Found {len(writable_services)} world-writable systemd services!\n")
            services_str = "\n".join(writable_services[:5])
            if len(writable_services) > 5:
                services_str += f"\n...and {len(writable_services) - 5} more."
                
            vulns.append({
                "title": "World-Writable Systemd Service",
                "description": f"Found systemd service files that are world-writable, allowing any user to modify the service execution path:\n{services_str}",
                "severity": "high",
                "mitre_id": "T1543.002"
            })
        else:
            sys.stderr.write("[+] No world-writable systemd services found.\n")
            
    except Exception as e:
        results.append({"action": "check_services", "error": str(e)})
        sys.stderr.write(f"[-] ERROR checking services: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1543.002",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_privesc(target), indent=2))
