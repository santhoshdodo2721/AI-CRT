#!/usr/bin/env python3
import subprocess
import shutil
import json
import sys
import os

def run_probe(target: str) -> dict:
    sys.stderr.write(f"[*] Starting HTTP Probe on {target}\n")
    if not target:
        return {"error": "target param required"}

    go_bin_path = os.path.expanduser("~/go/bin")
    
    tool_path = shutil.which("httpx")
    if not tool_path and os.path.exists(os.path.join(go_bin_path, "httpx")):
        tool_path = os.path.join(go_bin_path, "httpx")

    if not tool_path:
        sys.stderr.write("[!] httpx not found, falling back to curl.\n")
        return _curl_probe(target)

    targets = [t.strip() for t in target.split(",")]
    input_str = "\n".join(targets)

    cmd = [tool_path, "-json", "-title", "-tech-detect", "-status-code", "-follow-redirects"]
    try:
        sys.stderr.write(f"[DEBUG] Executing: {' '.join(cmd)}\n")
        result = subprocess.run(
            cmd, input=input_str, capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return {"error": "httpx timed out"}

    results = []
    for line in result.stdout.splitlines():
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            pass

    sys.stderr.write(f"[+] HTTP Probe complete. Found {len(results)} live web apps.\n")
    return {
        "target":  target,
        "results": results,
        "live":    len(results),
    }

def _curl_probe(target: str) -> dict:
    import urllib.request
    results = []
    for scheme in ["http", "https"]:
        url = f"{scheme}://{target}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                results.append({
                    "url":         url,
                    "status_code": resp.status,
                    "headers":     dict(resp.headers),
                })
        except Exception as e:
            results.append({"url": url, "error": str(e)})
    return {"target": target, "results": results, "tool": "curl_fallback"}

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    result = run_probe(target)
    print(json.dumps(result, indent=2))
