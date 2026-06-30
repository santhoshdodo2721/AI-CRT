#!/usr/bin/env python3
"""
MITRE ATT&CK Coverage Analyzer
Analyzes mapping and generates coverage reports
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict

class CoverageAnalyzer:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.mapping_file = self.base_path / "mapping.yaml"
        self.techniques_file = self.base_path / "techniques.json"
        self.cache_dir = self.base_path / "cache"
        self.attack_data_file = self.cache_dir / "attack_enterprise.json"
        
        self.mapping = self._load_yaml(self.mapping_file)
        self.techniques_layer = self._load_json(self.techniques_file) if self.techniques_file.exists() else {}
        self.attack_data = self._load_json(self.attack_data_file) if self.attack_data_file.exists() else {}
        
    def _load_yaml(self, path: Path) -> Dict:
        if path.exists():
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _load_json(self, path: Path) -> Dict:
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_all_attack_techniques(self) -> Dict[str, List[str]]:
        """Get all ATT&CK techniques grouped by tactic"""
        techniques_by_tactic = defaultdict(list)
        
        for obj in self.attack_data.get('objects', []):
            if obj.get('type') == 'attack-pattern':
                tech_id = obj.get('external_references', [{}])[0].get('external_id', '')
                for phase in obj.get('kill_chain_phases', []):
                    tactic = phase.get('phase_name', '')
                    if tactic:
                        techniques_by_tactic[tactic].append(tech_id)
        
        return dict(techniques_by_tactic)
    
    def get_covered_techniques(self) -> Dict[str, List[str]]:
        """Get covered techniques from mapping"""
        covered = defaultdict(set)
        
        modules = self.mapping.get('modules', {})
        for category, module_dict in modules.items():
            if not module_dict:
                continue
            for module_name, module_data in module_dict.items():
                if not module_data:
                    continue
                
                # Map category to ATT&CK tactic name
                tactic = self._category_to_tactic(category)
                if tactic:
                    tech_id = module_data.get('technique_id')
                    if tech_id:
                        covered[tactic].add(tech_id)
                    for subtech in module_data.get('subtechniques', []):
                        covered[tactic].add(subtech)
        
        return {k: list(v) for k, v in covered.items()}
    
    def _category_to_tactic(self, category: str) -> str:
        """Convert internal category name to ATT&CK tactic"""
        mapping = {
            'reconnaissance': 'reconnaissance',
            'vulnerability_scanning': 'reconnaissance',
            'initial_access': 'initial-access',
            'execution': 'execution',
            'persistence': 'persistence',
            'privilege_escalation': 'privilege-escalation',
            'defense_evasion': 'defense-evasion',
            'credential_access': 'credential-access',
            'discovery': 'discovery',
            'lateral_movement': 'lateral-movement',
            'collection': 'collection',
            'exfiltration': 'exfiltration',
            'command_and_control': 'command-and-control',
            'impact': 'impact'
        }
        return mapping.get(category, category)
    
    def calculate_coverage(self) -> Dict:
        """Calculate coverage percentages by tactic and overall"""
        all_techniques = self.get_all_attack_techniques()
        covered_techniques = self.get_covered_techniques()
        
        tactic_stats = {}
        total_all = 0
        total_covered = 0
        
        # Standard tactic order
        tactic_order = [
            'reconnaissance', 'resource-development', 'initial-access',
            'execution', 'persistence', 'privilege-escalation',
            'defense-evasion', 'credential-access', 'discovery',
            'lateral-movement', 'collection', 'exfiltration',
            'command-and-control', 'impact'
        ]
        
        for tactic in tactic_order:
            all_count = len(all_techniques.get(tactic, []))
            covered = set(covered_techniques.get(tactic, []))
            # Also check with underscore format
            covered.update(covered_techniques.get(tactic.replace('-', '_'), []))
            
            covered_count = len(covered)
            percentage = (covered_count / all_count * 100) if all_count > 0 else 0
            
            tactic_stats[tactic] = {
                'total': all_count,
                'covered': covered_count,
                'percentage': round(percentage, 1),
                'covered_ids': list(covered)
            }
            
            total_all += all_count
            total_covered += covered_count
        
        overall_percentage = (total_covered / total_all * 100) if total_all > 0 else 0
        
        return {
            'overall': {
                'total_techniques': total_all,
                'covered': total_covered,
                'percentage': round(overall_percentage, 1)
            },
            'by_tactic': tactic_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_module_technique_mapping(self) -> List[Dict]:
        """Get flat list of all module-to-technique mappings"""
        mappings = []
        
        modules = self.mapping.get('modules', {})
        for category, module_dict in modules.items():
            if not module_dict:
                continue
            for module_name, module_data in module_dict.items():
                if not module_data:
                    continue
                
                tactic = self._category_to_tactic(category)
                mappings.append({
                    'category': category,
                    'tactic': tactic,
                    'module': module_name,
                    'technique_id': module_data.get('technique_id'),
                    'technique_name': module_data.get('technique_name'),
                    'subtechniques': module_data.get('subtechniques', []),
                    'tool': module_data.get('tool'),
                    'risk_level': module_data.get('risk_level'),
                    'requires_approval': module_data.get('requires_approval', False),
                    'description': module_data.get('description')
                })
        
        return mappings
    
    def get_playbook_summary(self) -> List[Dict]:
        """Get summary of all playbooks"""
        playbooks = []
        
        for pb_name, pb_data in self.mapping.get('playbooks', {}).items():
            techniques = set()
            modules = []
            
            for phase in pb_data.get('phases', []):
                techniques.update(phase.get('techniques', []))
                modules.extend(phase.get('modules', []))
            
            playbooks.append({
                'name': pb_name,
                'display_name': pb_data.get('name', pb_name),
                'description': pb_data.get('description', ''),
                'phases': len(pb_data.get('phases', [])),
                'techniques': list(techniques),
                'technique_count': len(techniques),
                'modules': modules,
                'module_count': len(modules)
            })
        
        return playbooks
    
    def get_uncovered_techniques(self) -> Dict[str, List[str]]:
        """Find ATT&CK techniques not covered by any module"""
        all_techniques = self.get_all_attack_techniques()
        covered_techniques = self.get_covered_techniques()
        
        uncovered = {}
        
        for tactic, tech_ids in all_techniques.items():
            covered = set(covered_techniques.get(tactic, []))
            covered.update(covered_techniques.get(tactic.replace('-', '_'), []))
            
            uncovered_ids = [t for t in tech_ids if t not in covered]
            if uncovered_ids:
                uncovered[tactic] = uncovered_ids
        
        return uncovered
    
    def generate_report(self) -> Dict:
        """Generate comprehensive coverage report"""
        coverage = self.calculate_coverage()
        module_mappings = self.get_module_technique_mapping()
        playbooks = self.get_playbook_summary()
        uncovered = self.get_uncovered_techniques()
        
        # Count by risk level
        risk_counts = defaultdict(int)
        approval_counts = defaultdict(int)
        tool_counts = defaultdict(int)
        
        for m in module_mappings:
            risk_counts[m['risk_level']] += 1
            approval_counts['requires_approval' if m['requires_approval'] else 'auto'] += 1
            tool_counts[m['tool']] += 1
        
        return {
            'summary': {
                'overall_coverage': coverage['overall']['percentage'],
                'total_modules': len(module_mappings),
                'total_playbooks': len(playbooks),
                'tactics_with_coverage': len([t for t, s in coverage['by_tactic'].items() if s['covered'] > 0]),
                'tactics_total': len(coverage['by_tactic'])
            },
            'coverage': coverage,
            'modules': module_mappings,
            'playbooks': playbooks,
            'uncovered': uncovered,
            'statistics': {
                'by_risk_level': dict(risk_counts),
                'by_approval_requirement': dict(approval_counts),
                'by_tool': dict(tool_counts)
            },
            'generated_at': datetime.now().isoformat()
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MITRE ATT&CK Coverage Analyzer')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--uncovered', '-u', action='store_true', help='Show uncovered techniques')
    parser.add_argument('--modules', '-m', action='store_true', help='Show module mappings')
    parser.add_argument('--playbooks', '-p', action='store_true', help='Show playbook summary')
    
    args = parser.parse_args()
    
    analyzer = CoverageAnalyzer()
    
    if args.uncovered:
        uncovered = analyzer.get_uncovered_techniques()
        if args.json:
            print(json.dumps(uncovered, indent=2))
        else:
            print("\nUncovered ATT&CK Techniques:")
            print("="*50)
            for tactic, tech_ids in uncovered.items():
                print(f"\n{tactic.upper().replace('-', ' ')} ({len(tech_ids)} uncovered):")
                for tid in tech_ids[:10]:
                    print(f"  - {tid}")
                if len(tech_ids) > 10:
                    print(f"  ... and {len(tech_ids) - 10} more")
        return
    
    if args.modules:
        mappings = analyzer.get_module_technique_mapping()
        if args.json:
            print(json.dumps(mappings, indent=2))
        else:
            print("\nModule-to-Technique Mappings:")
            print("="*60)
            for m in mappings:
                print(f"\n[{m['category']}] {m['module']}")
                print(f"  Technique: {m['technique_id']} - {m['technique_name']}")
                print(f"  Tool: {m['tool']} | Risk: {m['risk_level']}")
                if m['subtechniques']:
                    print(f"  Sub-techniques: {', '.join(m['subtechniques'])}")
        return
    
    if args.playbooks:
        playbooks = analyzer.get_playbook_summary()
        if args.json:
            print(json.dumps(playbooks, indent=2))
        else:
            print("\nPlaybook Summary:")
            print("="*50)
            for pb in playbooks:
                print(f"\n📌 {pb['display_name']}")
                print(f"   Phases: {pb['phases']} | Techniques: {pb['technique_count']} | Modules: {pb['module_count']}")
                print(f"   {pb['description']}")
        return
    
    # Default: full report
    report = analyzer.generate_report()
    
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "="*60)
        print("MITRE ATT&CK COVERAGE REPORT")
        print("="*60)
        
        s = report['summary']
        print(f"\n📊 Overall Coverage: {s['overall_coverage']}%")
        print(f"   Modules Mapped: {s['total_modules']}")
        print(f"   Playbooks: {s['total_playbooks']}")
        print(f"   Tactics Covered: {s['tactics_with_coverage']}/{s['tactics_total']}")
        
        print("\n📈 Coverage by Tactic:")
        print("-"*60)
        for tactic, stats in report['coverage']['by_tactic'].items():
            bar_len = 30
            filled = int(stats['percentage'] / 100 * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"  {tactic[:20]:<20} [{bar}] {stats['percentage']:5.1f}% ({stats['covered']}/{stats['total']})")
        
        print("\n🛠️  By Tool:")
        for tool, count in report['statistics']['by_tool'].items():
            print(f"   {tool}: {count}")
        
        print("\n⚠️  By Risk Level:")
        for risk, count in report['statistics']['by_risk_level'].items():
            print(f"   {risk}: {count}")
        
        uncovered_count = sum(len(v) for v in report['uncovered'].values())
        print(f"\n❌ Uncovered Techniques: {uncovered_count}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    main()
EOF

chmod +x ~/CRT/redteam-lab/mitre/coverage.py
