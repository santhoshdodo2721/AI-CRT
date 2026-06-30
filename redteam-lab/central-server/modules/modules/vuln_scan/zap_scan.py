"""
Module: vuln_scan.zap_scan
Simulates an OWASP ZAP (Dynamic Application Security Testing) scan.
"""
import time
import random

def run(params: dict) -> dict:
    target = params.get("target")
    if not target:
        return {"error": "target param required"}
        
    time.sleep(2)  # Simulate scan delay
    
    # Simulate a variety of potential dynamic findings
    findings_pool = [
        {"name": "Cross-Site Scripting (Reflected)", "severity": "High", "confidence": "Medium", "path": "/search?q="},
        {"name": "Missing Anti-clickjacking Header", "severity": "Medium", "confidence": "High", "path": "/"},
        {"name": "Session ID in URL Rewrite", "severity": "Low", "confidence": "High", "path": "/login;jsessionid=..."},
        {"name": "Server Leaks Information via \"X-Powered-By\"", "severity": "Low", "confidence": "High", "path": "/"}
    ]
    
    # 80% chance of finding vulnerabilities
    found_vulns = []
    if random.random() < 0.8:
        # Pick 1 to 3 random findings
        num_findings = random.randint(1, 3)
        found_vulns = random.sample(findings_pool, k=num_findings)
        
    # Hardcode a finding for the local lab target
    if target in ["127.0.0.1", "localhost", "10.20.27.0/24"]:
        found_vulns.append({"name": "Cross-Site Scripting (Stored)", "severity": "High", "confidence": "High", "path": "/api/comments"})

    return {
        "target": target,
        "scanner": "OWASP ZAP",
        "alerts": found_vulns,
        "total_alerts": len(found_vulns),
        "status": "Vulnerable" if found_vulns else "Clean"
    }
