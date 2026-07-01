#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Starting Trivy scan on {target}\n")
    
    go_bin_path = os.path.expanduser("~/go/bin")
    
    tool_path = shutil.which("trivy")
    if not tool_path and os.path.exists(os.path.join(go_bin_path, "trivy")):
        tool_path = os.path.join(go_bin_path, "trivy")

    if not tool_path:
        return {"error": "Trivy not found. Install it and ensure it's in PATH."}

    cmd = [tool_path, "fs", target, "--format", "json"]
    
    try:
        sys.stderr.write(f"[DEBUG] Executing: {' '.join(cmd)}\n")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return {"error": "Trivy scan timed out"}

    vulns = []
    try:
        if result.stdout.strip():
            output_json = json.loads(result.stdout)
            results = output_json.get("Results", [])
            
            for r in results:
                target_file = r.get("Target", target)
                vulnerabilities = r.get("Vulnerabilities", [])
                for v in vulnerabilities:
                    vulns.append({
                        "template_id": v.get("VulnerabilityID", "unknown_cve"),
                        "type": "cve",
                        "severity": v.get("Severity", "UNKNOWN").lower(),
                        "matched_at": f"{target_file} ({v.get('PkgName', 'pkg')})",
                        "description": v.get("Title", v.get("Description", "No description"))
                    })
    except json.JSONDecodeError:
        return {"error": "Failed to parse Trivy JSON output", "raw": result.stdout[:200]}

    sys.stderr.write(f"[+] Trivy complete. Found {len(vulns)} vulnerabilities.\n")
    return {
        "target": target,
        "technique_id": "T1190",
        "vulns": [
            {
                "title": f"Trivy Finding: {v['template_id']}",
                "description": f"Found {v['severity']} vulnerability in {v['matched_at']}\n{v['description']}",
                "severity": v["severity"],
                "mitre_id": "T1190"
            } for v in vulns
        ],
        "vulnerabilities_found": len(vulns),
        "details": vulns
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(run_scan(target), indent=2))
