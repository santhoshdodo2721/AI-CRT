#!/usr/bin/env python3
import requests as http_req
import json
import sys

COMMON_ADMIN_PATHS = [
    "/admin",
    "/wp-admin",
    "/phpmyadmin",
    "/manager/html",
    "/server-status",
    "/dashboard"
]

def run_check(target: str) -> dict:
    if not target.startswith("http://") and not target.startswith("https://"):
        target = f"http://{target}"
        
    sys.stderr.write(f"[*] Checking for exposed admin interfaces on {target}\n")
    findings = []
    vulns = []
    
    for path in COMMON_ADMIN_PATHS:
        url = f"{target.rstrip('/')}{path}"
        try:
            r = http_req.get(url, timeout=5, allow_redirects=False)
            # If we get a 200 OK without auth, it's exposed
            if r.status_code == 200:
                findings.append({"path": path, "status": 200, "exposed": True})
                vulns.append({
                    "title": f"Exposed Admin Interface: {path}",
                    "description": f"Found an exposed administrative interface at {url} without authentication requirements.",
                    "severity": "high",
                    "mitre_id": "T1190"
                })
                sys.stderr.write(f"[+] EXPOSED: {url}\n")
            elif r.status_code in [401, 403]:
                # It exists but is protected
                findings.append({"path": path, "status": r.status_code, "exposed": False})
                sys.stderr.write(f"[-] PROTECTED: {url} ({r.status_code})\n")
        except http_req.exceptions.Timeout:
            sys.stderr.write(f"[-] TIMEOUT checking {url}\n")
        except Exception as e:
            sys.stderr.write(f"[-] ERROR checking {url}: {e}\n")

    return {
        "target": target,
        "technique_id": "T1190",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": findings
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print(json.dumps(run_check(target), indent=2))
