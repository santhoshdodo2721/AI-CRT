#!/usr/bin/env python3
import subprocess
import json
import sys

def run_evasion(target: str) -> dict:
    sys.stderr.write(f"[*] Checking local SIEM/EDR detection capabilities (T1070/Auditing) on {target}...\n")
    
    results = []
    vulns = []
    
    try:
        sys.stderr.write("[DEBUG] Querying journalctl for simulated attack markers...\n")
        
        # We search the system journal for traces of our previous tests
        # We'll look for "redteam_lab" or "base64" to see if the host logged our bash executions
        cmd = "journalctl -n 500 --no-pager | grep -iE 'redteam_lab|base64' 2>/dev/null"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        detected_logs = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        
        results.append({
            "action": "query_journal",
            "matches_found": len(detected_logs)
        })
        
        if detected_logs:
            sys.stderr.write(f"[+] Found {len(detected_logs)} traces in the system journal. Host is actively logging.\n")
            # This is actually a GOOD thing (Detection), but in red teaming, if we see our logs, 
            # it means we were caught, so we can log it as an informational finding.
            vulns.append({
                "title": "Simulated Attacks Logged (Caught)",
                "description": f"The host system is successfully logging our simulated attacks. {len(detected_logs)} traces were found in journalctl.",
                "severity": "info",
                "mitre_id": "T1070"
            })
        else:
            sys.stderr.write("[!] ALERT: No traces found in journalctl. Host logging may be blind or disabled.\n")
            vulns.append({
                "title": "Blind Logging (Evasion Successful)",
                "description": "Searched the local journal for attack markers but found none. The host may lack command line logging (e.g. auditd/sysmon), allowing successful defense evasion.",
                "severity": "medium",
                "mitre_id": "T1070"
            })
            
    except Exception as e:
        results.append({"action": "check_detection", "error": str(e)})
        sys.stderr.write(f"[-] ERROR checking detection: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1070",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_evasion(target), indent=2))
