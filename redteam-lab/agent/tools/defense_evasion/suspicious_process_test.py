#!/usr/bin/env python3
import subprocess
import json
import sys
import os
import shutil

def run_evasion(target: str) -> dict:
    sys.stderr.write(f"[*] Simulating Process Masquerading (T1036) on {target}...\n")
    
    results = []
    vulns = []
    success = False
    
    # We will copy the safe 'sleep' binary and name it 'kworker' 
    # to simulate a malicious process hiding as a kernel thread.
    masquerade_path = "/tmp/kworker_sim"
    original_binary = "/usr/bin/sleep"
    
    try:
        sys.stderr.write(f"[DEBUG] Copying {original_binary} to {masquerade_path}...\n")
        
        if os.path.exists(original_binary):
            shutil.copy2(original_binary, masquerade_path)
            os.chmod(masquerade_path, 0o755)
            
            sys.stderr.write(f"[DEBUG] Executing {masquerade_path} 1 in the background...\n")
            # Run the masqueraded binary for 1 second
            proc = subprocess.Popen([masquerade_path, "1"])
            
            # Wait for it to finish safely
            proc.communicate(timeout=3)
            success = proc.returncode == 0
            
            results.append({
                "action": "masquerade_process",
                "binary": masquerade_path,
                "success": success
            })
            
            if success:
                sys.stderr.write("[+] Masqueraded process execution successful.\n")
                vulns.append({
                    "title": "Process Masquerading Simulation",
                    "description": f"Successfully copied a benign binary to {masquerade_path} and executed it to simulate process masquerading (hiding as a kernel thread).",
                    "severity": "medium",
                    "mitre_id": "T1036"
                })
            else:
                sys.stderr.write("[-] Masqueraded process execution failed.\n")
        else:
            sys.stderr.write(f"[-] Original binary {original_binary} not found.\n")
            results.append({"action": "masquerade_process", "success": False, "error": "binary not found"})
            
    except Exception as e:
        results.append({"action": "masquerade_process", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during masquerading test: {e}\n")
    finally:
        # CLEANUP
        if os.path.exists(masquerade_path):
            sys.stderr.write(f"[DEBUG] Cleaning up {masquerade_path}...\n")
            os.remove(masquerade_path)
            
    return {
        "target": target if target else "local",
        "technique_id": "T1036",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_evasion(target), indent=2))
