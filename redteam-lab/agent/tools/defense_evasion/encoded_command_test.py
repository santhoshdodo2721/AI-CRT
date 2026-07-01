#!/usr/bin/env python3
import subprocess
import json
import sys
import base64

def run_evasion(target: str) -> dict:
    sys.stderr.write(f"[*] Simulating Defense Evasion (T1140) via Encoded Commands on {target}...\n")
    
    results = []
    vulns = []
    
    # Create a harmless payload, encode it, and execute
    safe_payload = "echo 'redteam_lab_base64_test_executed'"
    encoded_payload = base64.b64encode(safe_payload.encode()).decode('utf-8')
    
    try:
        sys.stderr.write("[DEBUG] Executing Base64 encoded payload...\n")
        cmd = f"echo '{encoded_payload}' | base64 -d | bash"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        
        success = r.returncode == 0
        output = r.stdout.strip()
        
        results.append({
            "action": "execute_base64",
            "command": cmd,
            "output": output,
            "success": success
        })
        
        if success and "redteam_lab" in output:
            sys.stderr.write(f"[+] Encoded command executed successfully: {output}\n")
            vulns.append({
                "title": "Encoded Command Execution",
                "description": f"Successfully executed a base64 encoded payload via bash piping to evade static command line detection.\nPayload: {cmd}",
                "severity": "medium",
                "mitre_id": "T1140"
            })
        else:
            sys.stderr.write("[-] Encoded command execution failed.\n")
            
    except Exception as e:
        results.append({"action": "execute_base64", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during encoded command test: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1140",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_evasion(target), indent=2))
