#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Starting Subdomain scan on {target}\n")
    
    domain = target
    if not domain:
        return {"error": "domain param required"}

    # Define common Go binary paths in case it's not strictly in PATH
    go_bin_path = os.path.expanduser("~/go/bin")
    
    tool = None
    tool_path = None
    
    for t in ["subfinder", "amass"]:
        which_path = shutil.which(t)
        if which_path:
            tool = t
            tool_path = which_path
            break
        elif os.path.exists(os.path.join(go_bin_path, t)):
            tool = t
            tool_path = os.path.join(go_bin_path, t)
            break

    if not tool:
        return {"error": "Neither subfinder nor amass found. Install subfinder: https://github.com/projectdiscovery/subfinder"}

    if tool == "subfinder":
        cmd = [tool_path, "-d", domain, "-silent"]
    else:
        cmd = [tool_path, "enum", "-d", domain, "-passive"]

    try:
        sys.stderr.write(f"[DEBUG] Executing: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"error": "Subdomain scan timed out after 5 minutes"}

    subdomains = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    
    sys.stderr.write(f"[+] Scan complete. Found {len(subdomains)} subdomains.\n")
    
    return {
        "target":     domain,
        "tool":       tool,
        "subdomains": subdomains,
        "count":      len(subdomains),
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    result = run_scan(target)
    print(json.dumps(result, indent=2))
