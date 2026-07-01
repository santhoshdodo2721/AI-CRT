class Analyzer:
    def __init__(self):
        pass

    def analyze(self, tool_output: dict) -> dict:
        """
        Takes raw JSON tool output and simulates an AI analyzing it.
        Extracts key findings and assigns a risk score.
        """
        analysis = {
            "summary": "No vulnerabilities found.",
            "risk_score": "Low",
            "findings": []
        }

        vulns = tool_output.get("vulns", [])
        if not vulns:
            return analysis

        analysis["findings"] = vulns
        
        # Calculate overall risk score based on highest severity
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        highest_weight = 0
        
        for v in vulns:
            w = severity_weights.get(v.get("severity", "info").lower(), 0)
            if w > highest_weight:
                highest_weight = w
                
        reverse_weights = {4: "Critical", 3: "High", 2: "Medium", 1: "Low", 0: "Info"}
        analysis["risk_score"] = reverse_weights.get(highest_weight, "Low")
        
        # Generate summary
        num_vulns = len(vulns)
        technique = tool_output.get("technique_id", "Unknown Technique")
        analysis["summary"] = f"Analyzed module output mapped to {technique}. Discovered {num_vulns} potential vulnerabilities with a max severity of {analysis['risk_score']}."
        
        return analysis
