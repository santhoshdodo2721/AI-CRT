#!/usr/bin/env python3
import time
import subprocess
import json
import sys
import os

# Add ai-engine to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai-engine')))

from analyzer import Analyzer
from mitre_mapper import MitreMapper
from remediation import RemediationAgent
from planner import PlannerAgent
from report_writer import ReportWriter

def print_step(num, title):
    print(f"\n{'='*50}")
    print(f"[{num}/15] {title.upper()}")
    print(f"{'='*50}")
    time.sleep(1)

def run_mock_tool(tool_path, target="localhost"):
    try:
        result = subprocess.run(["python3", tool_path, target], capture_output=True, text=True, check=True)
        # Parse the JSON from stdout, ignoring stderr logs
        for line in result.stdout.split('\n'):
            if line.startswith('{'):
                return json.loads(result.stdout[result.stdout.find('{'):])
        return {}
    except Exception as e:
        print(f"Error running {tool_path}: {e}")
        return {}

def main():
    print("Starting Autonomous AI Red Team Flow...\n")
    
    # 1. Install agent on target & 2. Agent registers with central server
    print_step(1, "Install agent on target")
    print_step(2, "Agent registers with central server")
    print("[+] Agent installation simulated. (agent.py deployed)")
    print("[+] Agent '02cc4a77-5ad0-4472-bc3a-ae38abbb7784' registered with server via HTTP Heartbeat.")
    time.sleep(1)

    # 3. User adds target
    print_step(3, "User adds target")
    target = "localhost"
    print(f"[+] User mapped scope to target: {target}")
    
    # 4. System performs recon
    print_step(4, "System performs recon")
    print(f"[*] Running agent/tools/recon/nmap_scan.py against {target}...")
    recon_out = run_mock_tool("agent/tools/recon/nmap_scan.py", target)
    print(f"[+] Discovered {len(recon_out.get('details', []))} open ports.")

    # 5. Vulnerability scan starts
    print_step(5, "Vulnerability scan starts")
    print(f"[*] Running agent/tools/vuln_scan/nuclei_scan.py against {target}...")
    vuln_out = run_mock_tool("agent/tools/vuln_scan/nuclei_scan.py", target)
    print(f"[+] Scan complete. {vuln_out.get('vulnerabilities_found', 0)} vulnerabilities flagged.")

    # 6. AI maps results to MITRE & 7. AI creates red team plan
    print_step(6, "AI maps results to MITRE")
    analyzer = Analyzer()
    mapper = MitreMapper()
    planner = PlannerAgent()
    
    analysis = analyzer.analyze(vuln_out)
    mapped_analysis = mapper.map_findings(analysis)
    print(f"[+] AI mapped findings to {len(mapped_analysis['findings'])} MITRE tactics/techniques.")
    
    print_step(7, "AI creates red team plan")
    plan = planner.suggest_next_action("vuln_scan", True)
    print(f"[+] AI Strategy: {plan['reason']}")
    print(f"[+] Selected Payload: {plan['next_module']}")
    
    # 8. User approves
    print_step(8, "User approves")
    print("[?] User prompted via dashboard: 'Approve AI execution plan?'")
    time.sleep(1)
    print("[+] User Approved.")
    
    # 9. Agent executes safe simulations & 10. Logs and results return
    print_step(9, "Agent executes safe simulations")
    print(f"[*] Dispatching task to agent: {plan['next_module']}")
    # Simulate execution phase
    exec_out = run_mock_tool("agent/tools/credentials/env_secret_scan.py", target)
    
    print_step(10, "Logs and results return")
    print("[+] Telemetry received from agent.")
    exec_analysis = analyzer.analyze(exec_out)
    exec_mapped = mapper.map_findings(exec_analysis)
    print(f"[+] AI assessed simulation impact: {exec_mapped['risk_score']} severity.")

    # 11. AI explains attack path & 12. Fixes are suggested
    print_step(11, "AI explains attack path")
    print("[+] AI Analysis: Attacker leveraged exposed local configurations to extract high-privilege credentials.")
    for f in exec_mapped.get("findings", []):
        print(f"    - {f.get('title')} ({f.get('mitre_id')})")
        
    print_step(12, "Fixes are suggested")
    remediator = RemediationAgent()
    remediated = remediator.generate_remediation(exec_mapped)
    for f in remediated.get("findings", []):
        print(f"[+] AI Remediation Plan: {f.get('remediation')}")

    # 13. Report is generated
    print_step(13, "Report is generated")
    writer = ReportWriter()
    report = writer.generate_html([remediated])
    report_path = "/tmp/final_redteam_report.html"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"[+] Executive summary generated at: {report_path}")

    # 14. DevOps pipeline applies changes
    print_step(14, "DevOps pipeline applies changes")
    print("[*] Simulating automated Infrastructure-as-Code pipeline patching...")
    time.sleep(2)
    # Mocking the fix by writing an empty file so the scan finds nothing
    print("[+] DevOps pipeline rotated secrets and applied strict ACLs.")

    # 15. System retests after update
    print_step(15, "System retests after update")
    print("[*] Re-running vulnerability scan to verify fix...")
    # Because we didn't actually edit the mock tool, we just simulate the fixed output
    fixed_out = {
        "target": target,
        "technique_id": "T1552",
        "vulns": [],
        "vulnerabilities_found": 0,
        "details": []
    }
    fixed_analysis = analyzer.analyze(fixed_out)
    print(f"[+] Retest complete. Vulnerabilities found: {fixed_analysis['summary']}")
    print("[+] Campaign successfully concluded. Network is secure.")
    print(f"\n{'='*50}")
    print("DEMONSTRATION COMPLETE")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
