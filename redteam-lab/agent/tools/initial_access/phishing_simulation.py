#!/usr/bin/env python3
import subprocess
import json
import sys

def check_dns_record(domain: str, record_type: str) -> str:
    try:
        result = subprocess.run(["dig", "+short", record_type, domain], capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception:
        return ""

def run_check(target: str) -> dict:
    # Clean target to just be a domain name
    domain = target.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    
    sys.stderr.write(f"[*] Simulating phishing campaign checks against {domain}\n")
    findings = []
    vulns = []
    
    sys.stderr.write("[DEBUG] Checking SPF...\n")
    spf_records = check_dns_record(domain, "TXT")
    has_spf = "v=spf1" in spf_records.lower()
    
    sys.stderr.write("[DEBUG] Checking DMARC...\n")
    dmarc_records = check_dns_record(f"_dmarc.{domain}", "TXT")
    has_dmarc = "v=dmarc1" in dmarc_records.lower()
    
    if not has_spf:
        vulns.append({
            "title": "Missing SPF Record",
            "description": f"Domain {domain} lacks a Sender Policy Framework (SPF) record, making it susceptible to email spoofing.",
            "severity": "medium",
            "mitre_id": "T1566"
        })
        findings.append({"check": "SPF", "status": "missing"})
    else:
        findings.append({"check": "SPF", "status": "present"})
        
    if not has_dmarc:
        vulns.append({
            "title": "Missing DMARC Record",
            "description": f"Domain {domain} lacks a DMARC record, increasing susceptibility to phishing simulations.",
            "severity": "medium",
            "mitre_id": "T1566"
        })
        findings.append({"check": "DMARC", "status": "missing"})
    else:
        findings.append({"check": "DMARC", "status": "present"})

    sys.stderr.write(f"[+] Phishing simulation checks complete. Found {len(vulns)} vulnerabilities.\n")
    
    return {
        "target": target,
        "technique_id": "T1566",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": findings
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example.com"
    print(json.dumps(run_check(target), indent=2))
