#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import uuid

def run_persistence(target: str) -> dict:
    marker = f"redteam_lab_persistence_test_{uuid.uuid4().hex[:8]}"
    sys.stderr.write(f"[*] Testing Persistence (T1053.003) via Cron on {target}...\n")
    
    results = []
    vulns = []
    success = False
    
    try:
        # 1. Read existing crontab
        sys.stderr.write("[DEBUG] Reading existing crontab...\n")
        existing = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True).stdout
        lines = existing.splitlines() if existing else []
        
        # 2. Add our harmless test cron (runs every minute, writes to /dev/null)
        test_cron = f"* * * * * echo '{marker}' > /dev/null"
        lines.append(test_cron)
        new_cron = "\n".join(lines) + "\n"
        
        # 3. Install it
        sys.stderr.write("[DEBUG] Installing temporary crontab...\n")
        proc = subprocess.run("crontab -", shell=True, input=new_cron, capture_output=True, text=True)
        
        if proc.returncode == 0:
            sys.stderr.write("[+] Temporarily installed persistence cron.\n")
            
            # 4. Verify it's there
            verify = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True).stdout
            success = marker in verify
            
            results.append({
                "action": "install_cron",
                "marker": marker,
                "success": success
            })
            
            if success:
                sys.stderr.write("[+] Cron persistence verified successfully.\n")
                vulns.append({
                    "title": "Cron Persistence Simulation",
                    "description": "Successfully simulated persistence by temporarily installing a cron job.",
                    "severity": "medium",
                    "mitre_id": "T1053.003"
                })
            
            # 5. CLEANUP: Remove our line and restore original crontab
            sys.stderr.write("[DEBUG] Cleaning up temporary crontab...\n")
            clean_lines = [l for l in verify.splitlines() if marker not in l]
            if clean_lines:
                clean_cron = "\n".join(clean_lines) + "\n"
                subprocess.run("crontab -", shell=True, input=clean_cron, capture_output=True, text=True)
            else:
                subprocess.run("crontab -r", shell=True, capture_output=True, text=True)
                
            sys.stderr.write("[+] Cleaned up test cron successfully.\n")
        else:
            sys.stderr.write("[-] Failed to install cron.\n")
            results.append({"action": "install_cron", "error": proc.stderr})
            
    except Exception as e:
        results.append({"action": "cron_persistence", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during cron test: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1053.003",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_persistence(target), indent=2))
