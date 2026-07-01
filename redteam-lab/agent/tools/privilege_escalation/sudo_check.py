#!/usr/bin/env python3
import subprocess
import json
import sys

def run_privesc(target: str) -> dict:
    sys.stderr.write(f"[*] Checking Sudo Misconfigurations (T1548.003) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        sys.stderr.write("[DEBUG] Running sudo -n -l...\n")
        r = subprocess.run("sudo -n -l 2>&1", shell=True, capture_output=True, text=True, timeout=5)
        output = r.stdout.strip()
        
        results.append({
            "action": "check_sudo",
            "output": output
        })
        
        if "may run the following commands" in output.lower():
            if "(root)" in output.lower() or "(all)" in output.lower() or "nopasswd:" in output.lower():
                sys.stderr.write("[!] ALERT: Sudo misconfiguration detected!\n")
                vulns.append({
                    "title": "Sudo Privilege Misconfiguration",
                    "description": f"User has potentially exploitable passwordless sudo rights.\nOutput:\n{output}",
                    "severity": "high",
                    "mitre_id": "T1548.003"
                })
            else:
                sys.stderr.write("[+] Sudo privileges found, but no immediate passwordless risk detected.\n")
        else:
            sys.stderr.write("[-] No passwordless sudo privileges found.\n")
            
    except Exception as e:
        results.append({"action": "check_sudo", "error": str(e)})
        sys.stderr.write(f"[-] ERROR checking sudo: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1548.003",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_privesc(target), indent=2))
