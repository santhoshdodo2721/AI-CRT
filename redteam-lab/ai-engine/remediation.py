class RemediationAgent:
    def __init__(self):
        # A simple knowledge base of fixes based on technique IDs
        self.knowledge_base = {
            "T1078": "Audit all local accounts and disable default/guest accounts. Implement strong password policies and MFA.",
            "T1190": "Apply security patches immediately to public-facing applications. Implement a WAF to block common exploits.",
            "T1552.001": "Remove hardcoded credentials from configuration files. Rotate any exposed secrets immediately and use a secure vault (e.g., AWS Secrets Manager, HashiCorp Vault).",
            "T1552.004": "Do not store sensitive tokens in environment variables where they can be dumped. Use short-lived IAM roles instead of long-lived access keys.",
            "T1046": "Implement network segmentation. Restrict access to lateral movement ports (SSH, SMB, RDP) using strict firewall rules or security groups.",
            "T1041": "Implement strict egress filtering on firewalls. Block outbound traffic on unnecessary ports and inspect HTTP/HTTPS traffic using a proxy.",
            "T1567": "Configure Data Loss Prevention (DLP) solutions to inspect outbound web traffic for sensitive data signatures.",
            "T1486": "Maintain offline, immutable backups. Implement EDR to catch rapid file modification heuristics indicative of ransomware.",
            "T1496": "Monitor CPU usage anomalies. Restrict the ability of generic accounts to spawn high-compute processes.",
            "T1489": "Restrict permissions to stop critical services to high-tier administrators only. Monitor service state changes in SIEM.",
        }

    def generate_remediation(self, mapped_analysis: dict) -> dict:
        """
        Takes the mapped analysis and appends specific remediation advice.
        """
        for finding in mapped_analysis.get("findings", []):
            tid = finding.get("mitre_id")
            if tid in self.knowledge_base:
                finding["remediation"] = self.knowledge_base[tid]
            else:
                finding["remediation"] = f"General Advice: Review the MITRE mitigation strategies for {tid}. Ensure principle of least privilege, segment networks, and keep software updated."
                
        return mapped_analysis
