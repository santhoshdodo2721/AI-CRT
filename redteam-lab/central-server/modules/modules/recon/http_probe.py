"""
Module: recon.http_probe
Probes HTTP/HTTPS services using httpx.
Install: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
"""
import subprocess
import shutil
import json


def run(params: dict) -> dict:
    target = params.get("target")
    if not target:
        return {"error": "target param required"}

    if not shutil.which("httpx"):
        # Fallback: use curl
        return _curl_probe(target)

    # Build target list – accept comma-separated or single
    targets = [t.strip() for t in target.split(",")]
    input_str = "\n".join(targets)

    cmd = ["httpx", "-json", "-title", "-tech-detect", "-status-code", "-follow-redirects"]
    try:
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

    return {
        "target":  target,
        "results": results,
        "live":    len(results),
    }


def _curl_probe(target: str) -> dict:
    """Minimal fallback when httpx is not installed."""
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
