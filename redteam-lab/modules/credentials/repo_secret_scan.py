#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import re

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Scanning local git repository history for exposed secrets (T1552.001) on {target}...\n")
    
    results = []
    vulns = []
    
    if not os.path.exists(".git"):
        sys.stderr.write("[-] No .git directory found in current working directory.\n")
        return {
            "target": target if target else "local",
            "technique_id": "T1552.001",
            "vulns": vulns,
            "vulnerabilities_found": 0,
            "details": [{"error": "Not a git repository"}]
        }
        
    try:
        sys.stderr.write("[DEBUG] Running git log -S search...\n")
        
        # Search git history for common secret keywords
        keywords = ["password=", "api_key=", "secret=", "token="]
        
        for kw in keywords:
            cmd = f"git log -p -S'{kw}' --max-count=50"
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            
            if r.returncode == 0 and r.stdout.strip():
                # We found traces of this keyword in the git history
                results.append({
                    "keyword": kw,
                    "found_in_history": True
                })
                
                sys.stderr.write(f"[!] ALERT: Found keyword '{kw}' in git commit history!\n")
                
                vulns.append({
                    "title": "Secret Found in Git History",
                    "description": f"Found traces of the keyword `{kw}` in the local git repository history. This indicates a secret may have been committed and is exposed in the `.git` directory.",
                    "severity": "high",
                    "mitre_id": "T1552.001"
                })
            else:
                results.append({
                    "keyword": kw,
                    "found_in_history": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during git repo scan: {e}\n")
        
    if not vulns:
        sys.stderr.write("[+] No exposed secrets detected in local git history.\n")
        
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
