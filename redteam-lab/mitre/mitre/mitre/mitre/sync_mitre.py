#!/usr/bin/env python3
"""
MITRE ATT&CK Data Synchronizer
Downloads and parses ATT&CK STIX data for local use
"""

import json
import requests
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

ATTACK_STIX_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"

class MitreSync:
def __init__(self, cache_dir: str = None):
self.base_path = Path(__file__).parent
self.cache_dir = Path(cache_dir) if cache_dir else self.base_path / "cache"
self.cache_dir.mkdir(exist_ok=True)

self.techniques_file = self.cache_dir / "attack_enterprise.json"
self.parsed_file = self.base_path / "techniques.json"
self.mapping_file = self.base_path / "mapping.yaml"

def download_attack_data(self, force: bool = False) -> bool:
"""Download ATT&CK STIX data from GitHub"""
if self.techniques_file.exists() and not force:
    print(f"[+] Using cached ATT&CK data: {self.techniques_file}")
    return True
    
    print(f"[*] Downloading ATT&CK STIX data from MITRE...")
    try:
    response = requests.get(ATTACK_STIX_URL, timeout=60)
    response.raise_for_status()
    
    with open(self.techniques_file, 'w') as f:
    json.dump(response.json(), f)
    
    print(f"[+] Downloaded and cached: {self.techniques_file}")
    return True
    except Exception as e:
    print(f"[-] Failed to download: {e}")
    return False
    
    def parse_attack_data(self) -> Dict:
    """Parse STIX data into usable format"""
    if not self.techniques_file.exists():
        return {}
        
        with open(self.techniques_file, 'r') as f:
        stix_data = json.load(f)
        
        techniques = {}
        tactics = {}
        subtechniques = {}
        
        for obj in stix_data.get('objects', []):
            obj_type = obj.get('type')
            
            if obj_type == 'attack-pattern':
                technique_id = obj.get('external_references', [{}])[0].get('external_id', '')
                name = obj.get('name', '')
                description = obj.get('description', '')
                kill_chain_phases = obj.get('kill_chain_phases', [])
                
                # Determine if sub-technique
                is_subtechnique = '.' in technique_id
                
                tactic_ids = [phase.get('phase_name', '') for phase in kill_chain_phases]
                
                technique_data = {
                'id': technique_id,
                'name': name,
                'description': description,
                'tactics': tactic_ids,
                'is_subtechnique': is_subtechnique,
                'parent': technique_id.split('.')[0] if is_subtechnique else None
                }
                
                if is_subtechnique:
                    subtechniques[technique_id] = technique_data
                    else:
                    techniques[technique_id] = technique_data
                    
                    elif obj_type == 'x-mitre-tactic':
                    tactic_id = obj.get('x_mitre_shortname', '')
                    tactics[tactic_id] = {
                    'id': obj.get('id', ''),
                    'name': obj.get('name', ''),
                    'shortname': tactic_id,
                    'order': obj.get('x_mitre_order', 0)
                    }
                    
                    return {
                    'techniques': techniques,
                    'subtechniques': subtechniques,
                    'tactics': tactics,
                    'last_sync': datetime.now().isoformat()
                    }
                    
                    def generate_navigator_layer(self, parsed_data: Dict = None) -> Dict:
                    """Generate ATT&CK Navigator compatible layer from mapping"""
                    if parsed_data is None:
                        parsed_data = self.parse_attack_data()
                        
                        # Load our module mapping
                        mapping = {}
                        if self.mapping_file.exists():
                            with open(self.mapping_file, 'r') as f:
                            mapping = yaml.safe_load(f) or {}
                            
                            techniques_list = []
                            all_mapped_ids = set()
                            
                            # Extract techniques from module mapping
                            modules = mapping.get('modules', {})
                            for tactic_category, module_dict in modules.items():
                            if not module_dict:
                                continue
                                for module_name, module_data in module_dict.items():
                                if not module_data:
                                    continue
                                    
                                    tech_id = module_data.get('technique_id')
                                    if tech_id:
                                        # Normalize tactic name for navigator
                                        nav_tactic = tactic_category.replace('_', '-')
                                        if nav_tactic == 'vulnerability-scanning':
                                            nav_tactic = 'reconnaissance'
                                            elif nav_tactic == 'credential-access':
                                            nav_tactic = 'credential-access'
                                            
                                            # Main technique
                                            techniques_list.append({
                                                    "techniqueID": tech_id,
                                                    "tactic": nav_tactic,
                                                    "score": 100,
                                                    "color": "#66ff66",
                                                    "comment": f"{module_name}: {module_data.get('description', '')}",
                                                    "enabled": True,
                                                    "metadata": [
                                                    {"name": "module", "value": module_name},
                                                    {"name": "tool", "value": module_data.get('tool', 'custom')},
                                                    {"name": "risk", "value": module_data.get('risk_level', 'low')}
                                                    ]
                                                })
                                            all_mapped_ids.add(tech_id)
                                            
                                            # Sub-techniques
                                            for subtech_id in module_data.get('subtechniques', []):
                                                techniques_list.append({
                                                        "techniqueID": subtech_id,
                                                        "tactic": nav_tactic,
                                                        "score": 100,
                                                        "color": "#66ff66",
                                                        "comment": f"{module_name} (sub-technique)",
                                                        "enabled": True
                                                    })
                                                all_mapped_ids.add(subtech_id)
                                                
                                                # Add techniques from playbooks that aren't in modules
                                                        playbooks = mapping.get('playbooks', {})
                                                        for pb_name, pb_data in playbooks.items():
                                                            for phase in pb_data.get('phases', []):
                                                                    for tech_id in phase.get('techniques', []):
                                                                            if tech_id not in all_mapped_ids:
                                                                                    techniques_list.append({
                                                                                                "techniqueID": tech_id,
                                                                                                "tactic": "initial-access",  # Default, will be overridden by navigator
                                                                                                "score": 50,
                                                                                                "color": "#ffff66",
                                                                                                "comment": f"Planned in {pb_name}",
                                                                                                "enabled": True
                                                                                        })
                                                                                    all_mapped_ids.add(tech_id)
                                                                    
                                                                    layer = {
                                                                        "type": "attack-pattern",
                                                                        "name": "Red Team Lab - Module Coverage",
                                                                        "description": f"MITRE ATT&CK coverage based on implemented modules. Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                                                                        "domain": "enterprise-attack",
                                                                        "versions": {
                                                                            "attack": "14.1",
                                                                            "navigator": "4.9.1",
                                                                            "layer": "4.5"
                                                                        },
                                                                        "techniques": techniques_list,
                                                                        "legendItems": [
                                                                            {"label": "✅ Covered (Module Implemented)", "color": "#66ff66", "order": 1},
                                                                            {"label": "🟡 Planned (In Playbook)", "color": "#ffff66", "order": 2},
                                                                            {"label": "❌ Not Covered", "color": "#ff6666", "order": 3}
                                                                        ],
                                                                        "filters": {
                                                                            "platforms": ["Linux", "Windows", "macOS"],
                                                                            "stages": ["act"]
                                                                        },
                                                                        "sorting": 0,
                                                                        "viewMode": 0,
                                                                        "hideDisabled": False,
                                                                        "showTacticRowBackground": True,
                                                                        "tacticRowBackground": "#205080",
                                                                        "selectTechniquesAcrossTactics": True,
                                                                        "metadata": [
                                                                            {"name": "Total Techniques Covered", "value": str(len(techniques_list))},
                                                                            {"name": "Unique Technique IDs", "value": str(len(all_mapped_ids))},
                                                                            {"name": "Modules Mapped", "value": str(sum(len(m) for m in modules.values() if m))},
                                                                            {"name": "Playbooks Defined", "value": str(len(playbooks))},
                                                                            {"name": "Generated By", "value": "Red Team Lab - sync_mitre.py"}
                                                                        ]
                                                                    }
                                                                    
                                                                    return layer
                                                                
                                                                def sync(self, force_download: bool = False) -> Dict:
                                                                    """Full sync: download, parse, generate layer"""
                                                                    results = {
                                                                        'downloaded': False,
                                                                        'parsed': False,
                                                                        'techniques_count': 0,
                                                                        'tactics_count': 0,
                                                                        'layer_generated': False,
                                                                        'layer_techniques': 0,
                                                                        'errors': []
                                                                    }
                                                                    
                                                                    # Download
                                                                    if self.download_attack_data(force=force_download):
                                                                            results['downloaded'] = True
                                                                        
                                                                        # Parse
                                                                        parsed = self.parse_attack_data()
                                                                        if parsed:
                                                                                results['parsed'] = True
                                                                                results['techniques_count'] = len(parsed.get('techniques', {}))
                                                                                results['tactics_count'] = len(parsed.get('tactics', {}))
                                                                            
                                                                            # Generate Navigator layer
                                                                            layer = self.generate_navigator_layer(parsed)
                                                                            with open(self.parsed_file, 'w') as f:
                                                                                json.dump(layer, f, indent=2)
                                                                            
                                                                            results['layer_generated'] = True
                                                                            results['layer_techniques'] = len(layer.get('techniques', []))
                                                                            
                                                                            return results
                                                                        
                                                                        def get_technique_info(self, technique_id: str) -> Optional[Dict]:
                                                                            """Get info about a specific technique"""
                                                                            parsed = self.parse_attack_data()
                                                                            
                                                                            # Check main techniques
                                                                            if technique_id in parsed.get('techniques', {}):
                                                                                    return parsed['techniques'][technique_id]
                                                                                
                                                                                # Check sub-techniques
                                                                                if technique_id in parsed.get('subtechniques', {}):
                                                                                        return parsed['subtechniques'][technique_id]
                                                                                    
                                                                                    return None
                                                                                
                                                                                def get_techniques_by_tactic(self, tactic: str) -> List[Dict]:
                                                                                    """Get all techniques for a tactic"""
                                                                                    parsed = self.parse_attack_data()
                                                                                    results = []
                                                                                    
                                                                                    for tech_id, tech_data in parsed.get('techniques', {}).items():
                                                                                        if tactic in tech_data.get('tactics', []):
                                                                                                results.append(tech_data)
                                                                                        
                                                                                        return results
                                                                                    
                                                                                    def get_module_for_technique(self, technique_id: str) -> List[Dict]:
                                                                                        """Find which modules map to a technique"""
                                                                                        if not self.mapping_file.exists():
                                                                                                return []
                                                                                            
                                                                                            with open(self.mapping_file, 'r') as f:
                                                                                                mapping = yaml.safe_load(f) or {}
                                                                                            
                                                                                            results = []
                                                                                            modules = mapping.get('modules', {})
                                                                                            
                                                                                            for category, module_dict in modules.items():
                                                                                                if not module_dict:
                                                                                                        continue
                                                                                                    for module_name, module_data in module_dict.items():
                                                                                                        if not module_data:
                                                                                                                continue
                                                                                                            
                                                                                                            if module_data.get('technique_id') == technique_id:
                                                                                                                    results.append({
                                                                                                                                'category': category,
                                                                                                                                'module': module_name,
                                                                                                                                'tool': module_data.get('tool'),
                                                                                                                                'description': module_data.get('description'),
                                                                                                                                'risk_level': module_data.get('risk_level'),
                                                                                                                                'requires_approval': module_data.get('requires_approval', False)
                                                                                                                        })
                                                                                                                
                                                                                                                if technique_id in module_data.get('subtechniques', []):
                                                                                                                        results.append({
                                                                                                                                    'category': category,
                                                                                                                                    'module': module_name,
                                                                                                                                    'tool': module_data.get('tool'),
                                                                                                                                    'description': f"Sub-technique of {module_data.get('technique_name')}",
                                                                                                                                    'risk_level': module_data.get('risk_level'),
                                                                                                                                    'requires_approval': module_data.get('requires_approval', False)
                                                                                                                            })
                                                                                                            
                                                                                                            return results
                                                                                                    
                                                                                                    
                                                                                                    def main():
                                                                                                        import argparse
                                                                                                        
                                                                                                        parser = argparse.ArgumentParser(description='MITRE ATT&CK Data Synchronizer')
                                                                                                        parser.add_argument('--force', '-f', action='store_true', help='Force re-download')
                                                                                                        parser.add_argument('--info', '-i', type=str, help='Get info about a technique (e.g., T1059)')
                                                                                                        parser.add_argument('--tactic', '-t', type=str, help='List techniques for tactic (e.g., execution)')
                                                                                                        parser.add_argument('--modules-for', '-m', type=str, help='Find modules for technique ID')
                                                                                                        parser.add_argument('--stats', '-s', action='store_true', help='Show coverage stats')
                                                                                                        
                                                                                                        args = parser.parse_args()
                                                                                                        
                                                                                                        syncer = MitreSync()
                                                                                                        
                                                                                                        if args.info:
                                                                                                                info = syncer.get_technique_info(args.info)
                                                                                                                if info:
                                                                                                                        print(json.dumps(info, indent=2))
                                                                                                                    else:
                                                                                                                        print(f"Technique {args.info} not found")
                                                                                                                    return
                                                                                                                
                                                                                                                if args.tactic:
                                                                                                                        techniques = syncer.get_techniques_by_tactic(args.tactic)
                                                                                                                        print(f"\nTechniques for tactic '{args.tactic}': {len(techniques)}")
                                                                                                                        for t in techniques[:20]:  # Limit output
                                                                                                                                print(f"  {t['id']}: {t['name']}")
                                                                                                                            if len(techniques) > 20:
                                                                                                                                    print(f"  ... and {len(techniques) - 20} more")
                                                                                                                                return
                                                                                                                            
                                                                                                                            if args.modules_for:
                                                                                                                                    modules = syncer.get_module_for_technique(args.modules_for)
                                                                                                                                    if modules:
                                                                                                                                            print(f"\nModules mapped to {args.modules_for}:")
                                                                                                                                            for m in modules:
                                                                                                                                                    print(f"  [{m['category']}] {m['module']} (tool: {m.get('tool')})")
                                                                                                                                                    print(f"    {m.get('description')}")
                                                                                                                                            else:
                                                                                                                                                print(f"No modules mapped to {args.modules_for}")
                                                                                                                                            return
                                                                                                                                        
                                                                                                                                        if args.stats:
                                                                                                                                                results = syncer.sync()
                                                                                                                                                print("\n" + "="*50)
                                                                                                                                                print("MITRE ATT&CK Sync Statistics")
                                                                                                                                                print("="*50)
                                                                                                                                                print(f"Downloaded ATT&CK data:  {'✓' if results['downloaded'] else '✗'}")
                                                                                                                                                print(f"Parsed successfully:      {'✓' if results['parsed'] else '✗'}")
                                                                                                                                                print(f"Total ATT&CK techniques:  {results['techniques_count']}")
                                                                                                                                                print(f"Total ATT&CK tactics:     {results['tactics_count']}")
                                                                                                                                                print(f"Navigator layer saved:    {'✓' if results['layer_generated'] else '✗'}")
                                                                                                                                                print(f"Covered technique entries:{results['layer_techniques']}")
                                                                                                                                                print("="*50)
                                                                                                                                                return
                                                                                                                                            
                                                                                                                                            # Default: full sync
                                                                                                                                            print("[*] Starting MITRE ATT&CK sync...")
                                                                                                                                            results = syncer.sync(force_download=args.force)
                                                                                                                                            
                                                                                                                                            print("\n" + "="*50)
                                                                                                                                            print("Sync Complete")
                                                                                                                                            print("="*50)
                                                                                                                                            print(f"Downloaded:         {'✓' if results['downloaded'] else '✗ (using cache)'}")
                                                                                                                                            print(f"Parsed:             {'✓' if results['parsed'] else '✗'}")
                                                                                                                                            print(f"ATT&CK Techniques:  {results['techniques_count']}")
                                                                                                                                            print(f"ATT&CK Tactics:     {results['tactics_count']}")
                                                                                                                                            print(f"Layer Generated:    {'✓' if results['layer_generated'] else '✗'}")
                                                                                                                                            print(f"Your Coverage:      {results['layer_techniques']} entries")
                                                                                                                                            print(f"\nOutput: {syncer.parsed_file}")
                                                                                                                                            print("="*50)
                                                                                                                                        
                                                                                                                                        
                                                                                                                                        if __name__ == "__main__":
                                                                                                                                                main()
                                                                                                                                            EOF
                                                                                                                                            
                                                                                                                                            chmod +x ~/CRT/redteam-lab/mitre/sync_mitre.py
