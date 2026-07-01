#!/usr/bin/env python3
import json
import sys
from analyzer import Analyzer
from mitre_mapper import MitreMapper
from remediation import RemediationAgent
from report_writer import ReportWriter

def main():
    print("[*] Starting AI Engine Pipeline Test...")
    
    # Mock tool output (simulating output from Phase 9: priv_esc)
    mock_tool_output = {
        "target": "localhost",
        "technique_id": "T1078",
        "vulns": [
            {
                "title": "Default Password Detected",
                "description": "Found a default password 'admin:admin' on the internal web portal.",
                "severity": "high",
                "mitre_id": "T1078"
            }
        ],
        "vulnerabilities_found": 1,
        "details": [{"user": "admin", "pass": "admin"}]
    }

    # 1. Analyze
    analyzer = Analyzer()
    analysis = analyzer.analyze(mock_tool_output)
    print(f"[+] Analyzer Output: {analysis['summary']} (Risk: {analysis['risk_score']})")

    # 2. MITRE Map
    mapper = MitreMapper()
    mapped_analysis = mapper.map_findings(analysis)
    print(f"[+] MITRE Mapper: Mapped {len(mapped_analysis['findings'])} finding(s).")

    # 3. Remediate
    remediator = RemediationAgent()
    remediated_analysis = remediator.generate_remediation(mapped_analysis)
    print(f"[+] Remediation Agent: Generated fix: {remediated_analysis['findings'][0].get('remediation')[:50]}...")

    # 4. Report
    writer = ReportWriter()
    html_report = writer.generate_html([remediated_analysis])
    
    with open("/tmp/ai_report_test.html", "w") as f:
        f.write(html_report)
        
    print("[+] Report Writer: Saved test report to /tmp/ai_report_test.html")
    print("[*] Pipeline test completed successfully.")

if __name__ == "__main__":
    main()
