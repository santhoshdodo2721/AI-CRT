#!/usr/bin/env python3
import subprocess
import json
import sys

def run_privesc(target: str) -> dict:
    print("[*] Checking Privilege Escalation vectors (T1548)...")
    findings = []
    
    # Check 1: Sudo misconfigurations (Read-only, completely safe)
    print("[*] Checking sudo -l...")
    r = subprocess.run("sudo -n -l 2>&1", shell=True, capture_output=True, text=True, timeout=5)
    if "may run" in r.stdout.lower() or "(root)" in r.stdout.lower() or "(ALL)" in r.stdout.lower():
        findings.append({"type": "sudo_misconfig", "severity": "High", "detail": "User can run commands as root without password!"})
        print("[!] ALERT: Sudo misconfiguration detected!")
    else:
        print("[-] No sudo misconfigurations found.")

    # Check 2: SUID Binaries (Read-only)
    print("[*] Checking for SUID binaries...")
    r2 = subprocess.run("find /usr -perm -4000 -type f 2>/dev/null | head -15", shell=True, capture_output=True, text=True, timeout=10)
    suid_bins = [b for b in r2.stdout.splitlines() if b]
    if suid_bins:
        findings.append({"type": "suid_bins", "severity": "Medium", "detail": f"Found {len(suid_bins)} SUID binaries.", "bins": suid_bins})
        print(f"[+] Found {len(suid_bins)} SUID binaries.")
    else:
        print("[-] No unusual SUID binaries found.")

    risk = "Low"
    summary = "No obvious privilege escalation vectors found."
    if len(findings) > 0:
        risk = "High" if any(f['severity'] == 'High' for f in findings) else "Medium"
        summary = f"Found {len(findings)} potential privilege escalation vectors."

    return {
        "technique_id": "T1548.003",
        "technique_name": "Abuse Elevation Control: Sudo",
        "risk_level": risk,
        "summary": summary,
        "details": findings
    }

if __name__ == "__main__":
    print(json.dumps(run_privesc(sys.argv[1] if len(sys.argv) > 1 else "localhost"), indent=2))
