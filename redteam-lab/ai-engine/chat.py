class ChatAgent:
    def __init__(self):
        pass

    def answer_query(self, user_query: str, context: list) -> str:
        """
        Simulates an LLM answering a user's question about the dashboard findings.
        """
        query = user_query.lower()
        
        # Simple simulated keyword-based router
        if "remediation" in query or "fix" in query:
            return "To fix the issues found, prioritize applying security patches to your external facing services and implementing a Web Application Firewall. Also, ensure you rotate any exposed credentials found in your configurations."
        
        if "critical" in query or "high" in query:
            criticals = [f for f in context if f.get("risk_score") in ["Critical", "High"]]
            if criticals:
                return f"Yes, we found {len(criticals)} High/Critical issues. These should be addressed immediately as they could lead to full system compromise."
            return "No Critical or High issues were detected in the provided context."
            
        if "mitre" in query:
            return "The findings map to several MITRE ATT&CK tactics including Initial Access, Privilege Escalation, and Impact. Check the detailed report for specific technique IDs like T1078 or T1486."
            
        return f"I am the AI Red Team Assistant. Based on the {len(context)} findings provided, your network has some security gaps. Please review the specific remediation steps in the report for more details."
