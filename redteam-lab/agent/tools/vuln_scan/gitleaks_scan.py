#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os
import tempfile

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Starting Gitleaks scan on {target}\n")
    
    go_bin_path = os.path.expanduser("~/go/bin")
    
    tool_path = shutil.which("gitleaks")
    if not tool_path and os.path.exists(os.path.join(go_bin_path, "gitleaks")):
        tool_path = os.path.join(go_bin_path, "gitleaks")

    if not tool_path:
        return {"error": "Gitleaks not found. Install it via Go."}

    # Gitleaks writes to a file, so we'll use a temp file
    fd, temp_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    
    # Run gitleaks detect
    cmd = [tool_path, "detect", "--source", target, "--report-format", "json", "--report-path", temp_path, "--exit-code", "0"]
    
    try:
        sys.stderr.write(f"[DEBUG] Executing: {' '.join(cmd)}\n")
        subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        os.remove(temp_path)
        return {"error": "Gitleaks scan timed out"}

    vulns = []
    try:
        with open(temp_path, "r") as f:
            content = f.read()
            if content.strip():
                results = json.loads(content)
                for r in results:
                    vulns.append({
                        "template_id": r.get("RuleID", "unknown_secret"),
                        "type": "credential_exposure",
                        "severity": "high",  # secrets are usually high/critical
                        "matched_at": f"{r.get('File', target)}:{r.get('StartLine', 0)}",
                        "description": f"Found {r.get('Description', 'secret')} in commit {r.get('Commit', 'unknown')}"
                    })
    except Exception as e:
        sys.stderr.write(f"[!] Failed to parse Gitleaks output: {e}\n")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    sys.stderr.write(f"[+] Gitleaks complete. Found {len(vulns)} secrets.\n")
    return {
        "target": target,
        "technique_id": "T1552",
        "vulns": [
            {
                "title": f"Gitleaks Finding: {v['template_id']}",
                "description": f"Found {v['severity']} credential exposure at {v['matched_at']}\n{v['description']}",
                "severity": v["severity"],
                "mitre_id": "T1552"
            } for v in vulns
        ],
        "vulnerabilities_found": len(vulns),
        "details": vulns
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(run_scan(target), indent=2))
