#!/usr/bin/env python3
import json, yaml
from pathlib import Path
from collections import defaultdict

class Coverage:
    def __init__(self):
        self.base = Path(__file__).parent
        self.map = yaml.safe_load((self.base / "mapping.yaml").read_text()) if (self.base / "mapping.yaml").exists() else {}
        self.cache = self.base / "cache"

    def run(self):
        raw_file = self.cache / "attack_enterprise.json"
        if not raw_file.exists():
            print("[-] Run sync_mitre.py first!")
            return
        stix = json.loads(raw_file.read_text())
        all_t = defaultdict(list)
        for o in stix.get("objects", []):
            if o.get("type") == "attack-pattern":
                tid = o.get("external_references", [{}])[0].get("external_id", "")
                for p in o.get("kill_chain_phases", []):
                    all_t[p.get("phase_name", "")].append(tid)
        
        cov = defaultdict(set)
        tmap = {"reconnaissance": "reconnaissance", "initial_access": "initial-access", "execution": "execution", "defense_evasion": "defense-evasion", "lateral_movement": "lateral-movement"}
        for c, m in self.map.get("modules", {}).items():
            if not m: continue
            tac = tmap.get(c, c)
            for n, d in m.items():
                if not d: continue
                if d.get("technique_id"): cov[tac].add(d["technique_id"])
                for s in d.get("subtechniques", []): cov[tac].add(s)
        
        print()
        print("="*50)
        print("MITRE ATT&CK COVERAGE REPORT")
        print("="*50)
        total_a, total_c = 0, 0
        for tac in ["reconnaissance", "initial-access", "execution", "persistence", "privilege-escalation", "defense-evasion", "credential-access", "discovery", "lateral-movement", "collection", "impact"]:
            a = len(all_t.get(tac, []))
            c = len(cov.get(tac, set()))
            p = (c/a*100) if a > 0 else 0
            total_a += a; total_c += c
            bar = "#" * int(p/100*25) + "-" * (25 - int(p/100*25))
            if a > 0: print(f"  {tac[:18]:<18} [{bar}] {p:5.1f}%")
        print("-"*50)
        op = (total_c/total_a*100) if total_a else 0
        print(f"  OVERALL             [{'#' * int(op/100*25) + '-' * (25 - int(op/100*25))}] {op:5.1f}%")
        print("="*50)
        print()

if __name__ == "__main__":
    Coverage().run()