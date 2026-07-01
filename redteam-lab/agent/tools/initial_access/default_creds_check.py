#!/usr/bin/env python3
import requests as http_req
import json
import sys

# Safe, limited list of default credentials for HTTP checks
CREDS = [
    ("admin", "admin"),
    ("root", "root"),
    ("admin", "password"),
    ("user", "user")
]

def run_check(target: str) -> dict:
    if not target.startswith("http://") and not target.startswith("https://"):
        target = f"http://{target}"
        
    sys.stderr.write(f"[*] Checking default credentials on {target}\n")
    findings = []
    
    for user, pwd in CREDS:
        try:
            # Using a short timeout to prevent hanging on failed auth
            r = http_req.get(target, auth=(user, pwd), timeout=5)
            if r.status_code == 200:
                findings.append({"user": user, "pass": pwd, "status": "SUCCESS"})
                sys.stderr.write(f"[+] SUCCESS: {user}:{pwd}\n")
            elif r.status_code == 401:
                sys.stderr.write(f"[-] FAILED: {user}:{pwd} (401 Unauthorized)\n")
        except http_req.exceptions.Timeout:
            sys.stderr.write(f"[-] TIMEOUT checking {user}\n")
        except Exception as e:
            sys.stderr.write(f"[-] ERROR: {e}\n")
            break

    risk = "high" if len(findings) > 0 else "low"
    
    vulns = []
    for f in findings:
        vulns.append({
            "title": "Default Credentials Exposed",
            "description": f"Valid default credentials found: {f['user']}:{f['pass']}",
            "severity": "high",
            "mitre_id": "T1078.001"
        })
    
    return {
        "target": target,
        "technique_id": "T1078.001",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": findings
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print(json.dumps(run_check(target), indent=2))
