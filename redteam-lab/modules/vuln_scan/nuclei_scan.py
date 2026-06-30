#!/usr/bin/env python3
import subprocess
import json
import sys
import re

def strip_ansi(text):
    # Removes color codes like [92m
    ansi_escape = re.compile(r'\[[0-9;]*m')
    return ansi_escape.sub('', text)

def run_scan(target: str) -> dict:
    print(f"[*] Starting Nuclei scan on {target}")
    cmd = ["nuclei", "-u", target, "-timeout", "15"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        vulns = []
        pattern = r"\[([^\]]+)\]\s+\[([^\]]+)\]\s+\[([^\]]+)\]\s+(https?://[^\s]+)"
        
        for line in result.stdout.splitlines():
            match = re.search(pattern, line)
            if match:
                vulns.append({
                    "template_id": strip_ansi(match.group(1)),
                    "type": strip_ansi(match.group(2)),
                    "severity": strip_ansi(match.group(3)),
                    "matched_at": strip_ansi(match.group(4))
                })
        
        print(f"[+] Nuclei complete. Found {len(vulns)} vulnerabilities.")
        return {
            "target": target,
            "technique_id": "T1595.002",
            "vulnerabilities_found": len(vulns),
            "details": vulns
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    print(json.dumps(run_scan(target), indent=2))