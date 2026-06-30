"""
Module: vuln_scan.trivy_scan
Simulates a Trivy vulnerability scan against container images or filesystems.
"""
import time
import random

def run(params: dict) -> dict:
    target = params.get("target")
    if not target:
        return {"error": "target param required"}
        
    time.sleep(1.5)  # Simulate scan delay
    
    # Simulate finding CVEs
    cve_pool = [
        {"vulnerability_id": "CVE-2023-38545", "pkg_name": "curl", "severity": "HIGH", "installed_version": "8.3.0-r0", "fixed_version": "8.4.0-r0"},
        {"vulnerability_id": "CVE-2023-4911", "pkg_name": "glibc", "severity": "CRITICAL", "installed_version": "2.36-9", "fixed_version": "2.36-9+deb12u3"},
        {"vulnerability_id": "CVE-2022-40897", "pkg_name": "setuptools", "severity": "MEDIUM", "installed_version": "65.5.0", "fixed_version": "65.5.1"}
    ]
    
    found_vulns = []
    if random.random() < 0.7:
        num_findings = random.randint(1, len(cve_pool))
        found_vulns = random.sample(cve_pool, k=num_findings)
        
    if target in ["127.0.0.1", "localhost", "10.20.27.0/24"]:
        found_vulns.append({"vulnerability_id": "CVE-2021-44228", "pkg_name": "log4j-core", "severity": "CRITICAL", "installed_version": "2.14.1", "fixed_version": "2.15.0"})

    return {
        "target": target,
        "scanner": "Trivy",
        "vulnerabilities": found_vulns,
        "total_cves": len(found_vulns),
        "status": "Vulnerable" if found_vulns else "Clean"
    }
