k#!/usr/bin/env python3
import subprocess
import json
import sys
import os

def run_persistence(target: str) -> dict:
    marker = "redteam_lab_persistence_test"
    print(f"[*] Testing Persistence (T1053.003) via Cron...")
    
    try:
        # 1. Read existing crontab
        existing = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True).stdout
        lines = existing.splitlines() if existing else []
        
        # 2. Add our harmless test cron (runs every minute, writes to /dev/null)
        test_cron = f"* * * * * echo '{marker}' > /dev/null"
        lines.append(test_cron)
        new_cron = "\n".join(lines)
        
        # 3. Install it
        proc = subprocess.run("crontab -", shell=True, input=new_cron, capture_output=True, text=True)
        if proc.returncode != 0:
            return {"error": "Failed to install cron", "details": []}
        
        print("[+] Temporarily installed persistence cron.")
        
        # 4. Verify it's there
        verify = subprocess.run("crontab -l 2>/dev/null", shell=True, capture_output=True, text=True).stdout
        success = marker in verify
        
        # 5. CLEANUP: Remove our line and restore original crontab
        clean_lines = [l for l in verify.splitlines() if marker not in l]
        clean_cron = "\n".join(clean_lines)
        subprocess.run("crontab -", shell=True, input=clean_cron, capture_output=True, text=True)
        print("[+] Cleaned up test cron successfully.")
        
        return {
            "technique_id": "T1053.003",
            "technique_name": "Scheduled Task/Job: Cron",
            "risk_level": "Medium" if success else "Low",
            "summary": "Successfully simulated and cleaned up cron persistence." if success else "Cron test failed.",
            "details": [{"test": "cron_install", "success": success}]
        }
    except Exception as e:
        return {"error": str(e), "details": []}

if __name__ == "__main__":
    print(json.dumps(run_persistence(sys.argv[1] if len(sys.argv) > 1 else "localhost"), indent=2))
