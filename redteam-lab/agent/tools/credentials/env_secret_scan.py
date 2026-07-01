#!/usr/bin/env python3
import os
import re
import json
import sys

def mask_secret(secret: str) -> str:
    """Masks a secret to prevent logging it in plain text."""
    secret = secret.strip('\'"')
    if len(secret) <= 4:
        return "****"
    return secret[:4] + "*" * (len(secret) - 4)

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Scanning local directories for exposed secrets (T1552.001) on {target}...\n")
    
    results = []
    vulns = []
    
    # Safe regex patterns to find hardcoded secrets
    patterns = [
        (r'(?i)(?:password|passwd|pwd)\s*=\s*["\']?([^"\'\s]+)["\']?', 'Hardcoded Password'),
        (r'(?i)api_key\s*=\s*["\']?([^"\'\s]+)["\']?', 'Hardcoded API Key'),
        (r'(?i)secret\s*=\s*["\']?([^"\'\s]+)["\']?', 'Hardcoded Secret'),
        (r'(?i)token\s*=\s*["\']?([^"\'\s]+)["\']?', 'Hardcoded Token'),
        (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Exposed Private Key')
    ]
    
    # Limit scope to current dir and specific extensions to avoid heavy I/O
    scan_path = os.getcwd()
    valid_extensions = ('.py', '.env', '.yml', '.yaml', '.json', '.txt', '.conf', '.sh')
    
    sys.stderr.write(f"[DEBUG] Scanning {scan_path}...\n")
    
    try:
        for root, dirs, files in os.walk(scan_path):
            # Skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(valid_extensions):
                    fpath = os.path.join(root, file)
                    try:
                        with open(fpath, 'r', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                for pattern, desc in patterns:
                                    match = re.search(pattern, line)
                                    if match:
                                        # Handle private key multiline match vs single line group match
                                        secret_val = match.group(1) if len(match.groups()) > 0 and match.group(1) else match.group(0)
                                        masked = mask_secret(secret_val)
                                        
                                        relative_path = os.path.relpath(fpath, scan_path)
                                        
                                        finding = {
                                            "file": relative_path,
                                            "line": line_num,
                                            "type": desc,
                                            "match": masked
                                        }
                                        results.append(finding)
                                        
                                        sys.stderr.write(f"[!] Found {desc} in {relative_path}:{line_num}\n")
                                        
                                        vulns.append({
                                            "title": f"Exposed Secret in File: {desc}",
                                            "description": f"Found a hardcoded secret ({desc}) in local file `{relative_path}` on line {line_num}.\nMasked Value: {masked}",
                                            "severity": "high",
                                            "mitre_id": "T1552.001"
                                        })
                    except Exception as file_e:
                        sys.stderr.write(f"[DEBUG] Error reading {fpath}: {file_e}\n")
                        
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during scan: {e}\n")
        
    if not vulns:
        sys.stderr.write("[+] No exposed credentials found in scanned files.\n")
        
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
