#!/usr/bin/env python3
import subprocess
import json
import sys
import base64

def run_evasion(target: str) -> dict:
    print("[*] Simulating Defense Evasion (T1140) via Encoded Commands...")
    
    # Create a harmless payload, encode it, and execute
    safe_payload = "echo '[Evasion Test] Command executed successfully'"
    encoded_payload = base64.b64encode(safe_payload.encode()).decode('utf-8')
    
    results = []
    
    # Test 1: Base64 Decoded Execution
    try:
        cmd = f"echo '{encoded_payload}' | base64 -d | bash"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        results.append({
            "technique": "Base64 Encoded Command",
            "success": r.returncode == 0,
            "output": r.stdout.strip()
        })
        print(f"[+] Encoded command executed: {r.stdout.strip()}")
    except Exception as e:
        results.append({"technique": "Base64 Encoded Command", "success": False, "error": str(e)})

    # Test 2: Environment Variable Obfuscation
    try:
        cmd2 = "export EVIL_VAR='safe_test'; echo $EVIL_VAR"
        r2 = subprocess.run(cmd2, shell=True, capture_output=True, text=True, timeout=5)
        results.append({
            "technique": "Env Variable Obfuscation",
            "success": r2.returncode == 0,
            "output": r2.stdout.strip()
        })
    except Exception as e:
        results.append({"technique": "Env Variable Obfuscation", "success": False, "error": str(e)})

    return {
        "technique_id": "T1140",
        "technique_name": "Deobfuscate/Decode Files or Information",
        "risk_level": "Medium",
        "summary": f"Executed {len(results)} obfuscation techniques to test evasion capabilities.",
        "details": results
    }

if __name__ == "__main__":
    print(json.dumps(run_evasion(sys.argv[1] if len(sys.argv) > 1 else "localhost"), indent=2))
