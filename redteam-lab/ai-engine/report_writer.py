from datetime import datetime

class ReportWriter:
    def __init__(self):
        pass

    def generate_html(self, enriched_findings: list) -> str:
        """
        Generates an HTML report from a list of enriched findings (output from RemediationAgent).
        """
        html = f"""
        <html>
        <head>
            <title>AI Red Team Executive Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }}
                h1 {{ color: #2c3e50; }}
                .finding {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 5px solid #3498db; }}
                .critical {{ border-left-color: #e74c3c; }}
                .high {{ border-left-color: #e67e22; }}
                .medium {{ border-left-color: #f1c40f; }}
                .low {{ border-left-color: #2ecc71; }}
                .mitre {{ background: #eee; padding: 10px; font-size: 0.9em; }}
                .remediation {{ background: #e8f8f5; padding: 10px; border-left: 3px solid #1abc9c; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <h1>AI Red Team Campaign Report</h1>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <hr>
        """
        
        if not enriched_findings:
            html += "<p>No vulnerabilities were detected during this campaign.</p>"
            
        for f in enriched_findings:
            severity = f.get('risk_score', 'Info').lower()
            html += f"""
            <div class="finding {severity}">
                <h2>{f.get('summary', 'Finding')}</h2>
                <p><strong>Risk Score:</strong> <span style="text-transform: uppercase;">{severity}</span></p>
            """
            
            for vuln in f.get('findings', []):
                html += f"""
                <h3>{vuln.get('title', 'Untitled')}</h3>
                <p>{vuln.get('description', '')}</p>
                <div class="mitre">
                    <strong>MITRE ATT&CK:</strong> {vuln.get('mitre_id')} - {vuln.get('mitre_name', 'Unknown')}<br>
                    <i>{vuln.get('mitre_description', '')[:200]}...</i>
                </div>
                <div class="remediation">
                    <strong>AI Remediation Plan:</strong><br>
                    {vuln.get('remediation', 'No specific remediation provided.')}
                </div>
                """
            html += "</div>"
            
        html += """
        </body>
        </html>
        """
        return html
