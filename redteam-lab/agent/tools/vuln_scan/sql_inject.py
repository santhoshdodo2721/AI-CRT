"""
Module: vuln_scan.sql_inject
Simulates an automated SQL Injection (SQLi) probe against a target web server.
"""
import random
import time

def run(params: dict) -> dict:
    target = params.get("target", "")
    
    if not target:
        return {"error": "target param required"}

    # Simulate testing delay
    time.sleep(2)
    
    payloads = [
        "' OR 1=1 --",
        "admin' --",
        "1; DROP TABLE users",
        "' UNION SELECT null, null, null --"
    ]
    
    # Simulate a vulnerability finding
    is_vulnerable = random.choice([True, False, False, False]) # 25% chance of finding
    
    if "127.0.0.1" in target or "localhost" in target:
        is_vulnerable = True
        
    results = []
    
    if is_vulnerable:
        successful_payload = random.choice(payloads)
        results.append({
            "vulnerability": "SQL Injection (SQLi)",
            "endpoint": f"http://{target}/api/users?id=",
            "payload": successful_payload,
            "evidence": "Database syntax error reflected in response or successful authentication bypass."
        })
        
    return {
        "target": target,
        "tool": "sqli_probe_sim",
        "vulnerabilities_found": results,
        "payloads_tested": len(payloads) * 5,
        "status": "Vulnerable" if is_vulnerable else "Secure"
    }
