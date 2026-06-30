"""
Module: vuln_scan.semgrep_scan
Simulates a Semgrep Static Application Security Testing (SAST) scan.
"""
import time
import random

def run(params: dict) -> dict:
    target = params.get("target")
    if not target:
        return {"error": "target param required"}
        
    time.sleep(2)  # Simulate scan delay
    
    # Simulate SAST findings
    rules_pool = [
        {"rule_id": "javascript.express.security.audit.xss.direct-response-write.direct-response-write", "message": "Untrusted input concatenated directly into the HTTP response", "severity": "WARNING"},
        {"rule_id": "python.django.security.injection.sql-injection.django-rawsql-used", "message": "Detected use of RawSQL which can lead to SQL injection", "severity": "ERROR"},
        {"rule_id": "generic.secrets.security.detected-aws-credentials", "message": "Hardcoded AWS credentials detected", "severity": "ERROR"}
    ]
    
    found_vulns = []
    if random.random() < 0.6:
        num_findings = random.randint(1, len(rules_pool))
        found_vulns = random.sample(rules_pool, k=num_findings)
        
    if target in ["127.0.0.1", "localhost", "10.20.27.0/24"]:
        found_vulns.append({"rule_id": "python.flask.security.injection.command.command-injection", "message": "Command injection vulnerability detected in os.system() call", "severity": "ERROR"})

    return {
        "target": target,
        "scanner": "Semgrep",
        "findings": found_vulns,
        "total_findings": len(found_vulns),
        "status": "Vulnerable" if found_vulns else "Clean"
    }
