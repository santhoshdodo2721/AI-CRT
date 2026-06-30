#!/usr/bin/env python3
import os
import re
import json
import sys

# Safe regex patterns to find hardcoded secrets
PATTERNS = [
    (r'(?i)password\s*=\s*["\']?([^"\']+)', 'Hardcoded Password'),
    (r'(?i)api_key\s*=\s*["\']?([^"\']+)', 'Hardcoded API Key'),
    (r'(?i)secret\s*=\s*["\']?([^"\']+)', 'Hardcoded Secret'),
    (r'(?i)token\s*=\s*["\']?([^"\']+)', 'Hardcoded Token'),
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Exposed Private Key')
]

def scan_directory(path: str) -> list:
    findings = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(('.py', '.env', '.yml', '.yaml', '.json', '.txt', '.conf')):
                fpath = os.path.join(root, file)
                try:
                    with open(fpath, 'r', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern, desc in PATTERNS:
                                match = re.search(pattern, line)
                                if match:
                                    # Mask the actual secret so we don't print it in plain text
                                    masked = match.group(0)[:20] + "..."
                                    findings.append({
                                        "file": fpath,
                                        "line": line_num,
                                        "type": desc,
                                        "match": masked
                                    })
                except Exception:
                    pass
    return findings

def run_scan(target: str) -> dict:
    # We scan our own modules directory as a safe Proof of Concept
    scan_path = "/home/dodo/CRT/redteam-lab/modules"
    print(f"[*] Scanning {scan_path} for exposed credentials (T1552.001)...")
    
    findings = scan_directory(scan_path)
    
    if findings:
        risk = "Medium"
        summary = f"Found {len(findings)} potential hardcoded secrets!"
    else:
        risk = "Low"
        summary = "No exposed credentials found in scanned directories."

    print(f"[+] Scan complete. Found {len(findings)} matches.")
    
    return {
        "technique_id": "T1552.001",
        "technique_name": "Unsecured Credentials: Credentials In Files",
        "risk_level": risk,
        "summary": summary,
        "details": findings
    }

if __name__ == "__main__":
    print(json.dumps(run_scan(sys.argv[1] if len(sys.argv) > 1 else "localhost"), indent=2))
