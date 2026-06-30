"""
Module: recon.subdomain_scan
Discovers subdomains using subfinder (preferred) or amass.
Install: go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
"""
import subprocess
import shutil


def run(params: dict) -> dict:
    domain = params.get("domain")
    if not domain:
        return {"error": "domain param required"}

    tool = None
    for t in ["subfinder", "amass"]:
        if shutil.which(t):
            tool = t
            break

    if not tool:
        return {"error": "Neither subfinder nor amass found. Install subfinder: https://github.com/projectdiscovery/subfinder"}

    if tool == "subfinder":
        cmd = ["subfinder", "-d", domain, "-silent"]
    else:
        cmd = ["amass", "enum", "-d", domain, "-passive"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"error": "Subdomain scan timed out after 5 minutes"}

    subdomains = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return {
        "domain":     domain,
        "tool":       tool,
        "subdomains": subdomains,
        "count":      len(subdomains),
    }
