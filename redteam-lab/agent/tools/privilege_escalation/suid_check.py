#!/usr/bin/env python3
import subprocess
import json
import sys
import os

def run_privesc(target: str) -> dict:
    sys.stderr.write(f"[*] Checking for SUID Binaries (T1548.001) on {target}...\n")
    
    results = []
    vulns = []
    
    # Common exploitable binaries from GTFOBins
    gtfobins = ['bash', 'cp', 'find', 'vim', 'nmap', 'python', 'ruby', 'perl', 'awk', 'less', 'more', 'tar']
    
    try:
        sys.stderr.write("[DEBUG] Running find command for SUID binaries in /usr/bin...\n")
        # Restrict to /usr/bin to avoid long execution times in lab
        r = subprocess.run("find /usr/bin -perm -4000 -type f 2>/dev/null", shell=True, capture_output=True, text=True, timeout=10)
        
        suid_bins = [b.strip() for b in r.stdout.splitlines() if b.strip()]
        
        results.append({
            "action": "find_suid",
            "binaries": suid_bins
        })
        
        exploitable = []
        for b in suid_bins:
            basename = os.path.basename(b)
            if basename in gtfobins:
                exploitable.append(b)
                
        if exploitable:
            sys.stderr.write(f"[!] ALERT: Found {len(exploitable)} potentially exploitable SUID binaries!\n")
            vulns.append({
                "title": "Exploitable SUID Binaries",
                "description": f"Found SUID binaries that exist in GTFOBins and can likely be abused to escalate privileges:\n{', '.join(exploitable)}",
                "severity": "high",
                "mitre_id": "T1548.001"
            })
        else:
            sys.stderr.write(f"[+] Found {len(suid_bins)} SUID binaries, none appear immediately exploitable.\n")
            
    except Exception as e:
        results.append({"action": "check_suid", "error": str(e)})
        sys.stderr.write(f"[-] ERROR checking SUID: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1548.001",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_privesc(target), indent=2))
