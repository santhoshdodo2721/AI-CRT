import json
import os

class MitreMapper:
    def __init__(self, mitre_cache_path="/home/dodo/DODO/AI-CRT/redteam-lab/mitre/cache/attack_enterprise.json"):
        self.mitre_data = []
        if os.path.exists(mitre_cache_path):
            try:
                with open(mitre_cache_path, 'r') as f:
                    data = json.load(f)
                    self.mitre_data = data.get("objects", [])
            except Exception:
                pass

    def map_findings(self, analysis_dict: dict) -> dict:
        """
        Takes the analyzer's output and maps each finding to a MITRE technique name/description.
        """
        for finding in analysis_dict.get("findings", []):
            tid = finding.get("mitre_id")
            if not tid:
                continue
                
            technique_info = self._lookup_technique(tid)
            if technique_info:
                finding["mitre_name"] = technique_info.get("name", "Unknown")
                finding["mitre_description"] = technique_info.get("description", "No description available.")
            else:
                finding["mitre_name"] = "Lookup Failed"
                finding["mitre_description"] = "Could not find technique in local cache."
                
        return analysis_dict

    def _lookup_technique(self, tid: str) -> dict:
        for obj in self.mitre_data:
            if obj.get("type") == "attack-pattern":
                ext_refs = obj.get("external_references", [])
                for ref in ext_refs:
                    if ref.get("source_name") == "mitre-attack" and ref.get("external_id") == tid:
                        return obj
        return None
