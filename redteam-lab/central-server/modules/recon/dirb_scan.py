"""
Module: recon.dirb_scan
Simulates a directory brute force scan against a target web server.
"""
import random
import time
import re

def run(params: dict) -> dict:
    target = params.get("target", "")
    
    if not target:
        return {"error": "target param required"}

    # Simulate network delay
    time.sleep(1)
    
    # Common directories to simulate finding
    common_dirs = [
        "/admin", "/login", "/config.php", "/.git/HEAD", 
        "/backup.zip", "/phpmyadmin", "/api/v1/users", "/dashboard"
    ]
    
    # Randomly select a few directories that "exist"
    found_dirs = random.sample(common_dirs, k=random.randint(1, 4))
    
    results = []
    for d in found_dirs:
        status_code = random.choice([200, 401, 403])
        results.append({
            "path": d,
            "status": status_code,
            "url": f"http://{target}{d}" if not target.startswith("http") else f"{target}{d}"
        })
    
    # If it's a specific local test target, let's hardcode some interesting finds
    if "127.0.0.1" in target or "localhost" in target:
        results.append({
            "path": "/.env",
            "status": 200,
            "url": f"http://{target}/.env",
            "notes": "Sensitive environment file exposed!"
        })

    return {
        "target": target,
        "tool": "dirb_sim",
        "directories_found": results,
        "total_tested": 500,
        "total_found": len(results)
    }
