#!/usr/bin/env python3
import os
import json
import sys

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Scanning for exposed local configuration files (T1552.001) on {target}...\n")
    
    results = []
    vulns = []
    
    # Common sensitive configuration files
    target_files = [
        "~/.aws/credentials",
        "~/.kube/config",
        "~/.ssh/id_rsa",
        "~/.npmrc",
        "~/.docker/config.json",
        "~/.netrc"
    ]
    
    try:
        for tf in target_files:
            expanded_path = os.path.expanduser(tf)
            sys.stderr.write(f"[DEBUG] Checking {expanded_path}...\n")
            
            if os.path.exists(expanded_path):
                # Verify we can actually read it
                if os.access(expanded_path, os.R_OK):
                    sys.stderr.write(f"[!] ALERT: Found sensitive configuration file at {expanded_path}\n")
                    results.append({
                        "file": tf,
                        "exists": True,
                        "readable": True
                    })
                    vulns.append({
                        "title": "Exposed Cloud/Infrastructure Configuration File",
                        "description": f"Found an exposed, readable configuration file at `{tf}` that likely contains sensitive deployment credentials or private keys.",
                        "severity": "high",
                        "mitre_id": "T1552.001"
                    })
                else:
                    sys.stderr.write(f"[-] Found {expanded_path} but it is not readable.\n")
                    results.append({
                        "file": tf,
                        "exists": True,
                        "readable": False
                    })
            else:
                results.append({
                    "file": tf,
                    "exists": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during config scan: {e}\n")
        
    if not vulns:
        sys.stderr.write("[+] No exposed configuration files found.\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1552.001",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
