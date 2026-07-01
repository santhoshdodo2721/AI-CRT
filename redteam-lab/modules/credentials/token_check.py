#!/usr/bin/env python3
import os
import json
import sys

def mask_secret(secret: str) -> str:
    """Masks a secret to prevent logging it in plain text."""
    if len(secret) <= 4:
        return "****"
    return secret[:4] + "*" * (len(secret) - 4)

def run_scan(target: str) -> dict:
    sys.stderr.write(f"[*] Inspecting local environment variables for exposed tokens (T1552.004) on {target}...\n")
    
    results = []
    vulns = []
    
    # Common sensitive environment variable keys
    sensitive_keys = [
        "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
        "GITHUB_TOKEN", "GITLAB_TOKEN", "NVIDIA_API_KEY", "OPENAI_API_KEY",
        "DATABASE_URL", "SECRET_KEY", "SLACK_BOT_TOKEN", "DISCORD_TOKEN"
    ]
    
    try:
        sys.stderr.write("[DEBUG] Reading active environment variables...\n")
        
        for key in sensitive_keys:
            val = os.environ.get(key)
            if val:
                masked_val = mask_secret(val)
                sys.stderr.write(f"[!] ALERT: Found sensitive token exposed in environment variable: {key}\n")
                
                results.append({
                    "env_var": key,
                    "exposed": True,
                    "masked_value": masked_val
                })
                
                vulns.append({
                    "title": f"Exposed Token in Environment Variable: {key}",
                    "description": f"The sensitive token `{key}` is exposed in the active running environment. This could be stolen if the process memory is dumped or child processes inherit the environment.\nMasked Value: {masked_val}",
                    "severity": "high",
                    "mitre_id": "T1552.004"
                })
            else:
                results.append({
                    "env_var": key,
                    "exposed": False
                })
                
    except Exception as e:
        results.append({"error": str(e)})
        sys.stderr.write(f"[-] ERROR during environment scan: {e}\n")
        
    if not vulns:
        sys.stderr.write("[+] No exposed sensitive tokens found in the active environment.\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1552.004",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_scan(target), indent=2))
