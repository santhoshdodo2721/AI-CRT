#!/usr/bin/env python3
import json, requests, yaml
from pathlib import Path
from datetime import datetime

ATTACK_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

class MitreSync:
    def __init__(self):
        self.base = Path(__file__).parent
        self.cache = self.base / "cache"
        self.cache.mkdir(exist_ok=True)
        self.raw = self.cache / "attack_enterprise.json"
        self.layer = self.base / "techniques.json"
        self.mapping = self.base / "mapping.yaml"

    def download(self, force=False):
        if self.raw.exists() and not force:
            print("[+] Using cached ATT&CK data")
            return True
        print("[*] Downloading ATT&CK STIX data...")
        try:
            r = requests.get(ATTACK_URL, timeout=60)
            r.raise_for_status()
            self.raw.write_text(r.text)
            print("[+] Downloaded successfully")
            return True
        except Exception as e:
            print(f"[-] Download failed: {e}")
            return False

    def generate_layer(self):
        mapping = yaml.safe_load(self.mapping.read_text()) if self.mapping.exists() else {}
        techs = []
        tac_map = {"reconnaissance": "reconnaissance", "initial_access": "initial-access", "execution": "execution", "defense_evasion": "defense-evasion", "lateral_movement": "lateral-movement"}
        for cat, mods in mapping.get("modules", {}).items():
            if not mods: continue
            tactic = tac_map.get(cat, cat)
            for name, data in mods.items():
                if not data: continue
                tid = data.get("technique_id")
                if tid:
                    techs.append({"techniqueID": tid, "tactic": tactic, "score": 100, "color": "#66ff66", "comment": f"{name}: {data.get(chr(100)+chr(101)+chr(115)+chr(99)+chr(114)+chr(105)+chr(112)+chr(116)+chr(105)+chr(111)+chr(110), chr(63))}", "enabled": True})
                for s in data.get("subtechniques", []):
                    techs.append({"techniqueID": s, "tactic": tactic, "score": 100, "color": "#66ff66", "comment": f"{name} (sub-tech)", "enabled": True})
        out = {"type": "attack-pattern", "name": "Red Team Lab Coverage", "domain": "enterprise-attack", "versions": {"attack": "14.1", "navigator": "4.9.1"}, "techniques": techs, "legendItems": [{"label": "Covered", "color": "#66ff66"}], "filters": {"platforms": ["Linux", "Windows"]}}
        self.layer.write_text(json.dumps(out, indent=2))
        print(f"[+] Generated layer: {len(techs)} entries")

    def run(self, force=False):
        self.download(force)
        self.generate_layer()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("-f", "--force", action="store_true")
    MitreSync().run(force=p.parse_args().force)