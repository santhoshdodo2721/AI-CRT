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
    if not target.startswith("http"):
        target = f"http://{target}"
        
    print(f"[*] Checking default credentials on {target}")
    findings = []
    
    for user, pwd in CREDS:
        try:
            # Using a short timeout to prevent hanging on failed auth
            r = http_req.get(target, auth=(user, pwd), timeout=5)
            if r.status_code == 200:
                findings.append({"user": user, "pass": pwd, "status": "SUCCESS"})
                print(f"[+] SUCCESS: {user}:{pwd}")
            elif r.status_code == 401:
                print(f"[-] FAILED: {user}:{pwd} (401 Unauthorized)")
        except http_req.exceptions.Timeout:
            print(f"[-] TIMEOUT checking {user}")
        except Exception as e:
            print(f"[-] ERROR: {e}")
            break

    risk = "High" if len(findings) > 0 else "Low"
    summary = f"Found {len(findings)} valid default credentials." if findings else "No default credentials worked."
    
    return {
        "target": target,
        "technique_id": "T1078.001",
        "technique_name": "Default Accounts",
        "risk_level": risk,
        "summary": summary,
        "details": findings
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print(json.dumps(run_check(target), indent=2))
