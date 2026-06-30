#!/usr/bin/env python3
"""
MITRE ATT&CK Coverage Engine
- Loads mapping.yaml
- Computes coverage from completed tasks
- Generates heatmap / navigator layer JSON
- Tracks detection results per technique
"""
import json
import yaml
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

BASE_DIR   = Path(__file__).parent
MAPPING    = BASE_DIR / "mapping.yaml"
TECHNIQUES = BASE_DIR / "techniques.json"
RESULTS    = BASE_DIR / "coverage_results.json"

TACTIC_ORDER = [
    "reconnaissance", "resource-development", "initial-access", "execution",
    "persistence", "privilege-escalation", "defense-evasion", "credential-access",
    "discovery", "lateral-movement", "collection", "command-and-control",
    "exfiltration", "impact",
]

TACTIC_COLORS = {
    "reconnaissance":      "#6366f1",
    "initial-access":      "#f59e0b",
    "execution":           "#ef4444",
    "persistence":         "#8b5cf6",
    "privilege-escalation":"#ec4899",
    "defense-evasion":     "#14b8a6",
    "credential-access":   "#f97316",
    "discovery":           "#06b6d4",
    "lateral-movement":    "#84cc16",
    "collection":          "#a855f7",
    "exfiltration":        "#f43f5e",
    "impact":              "#dc2626",
}

SEVERITY_SCORE = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def load_mapping() -> dict:
    if not MAPPING.exists():
        return {}
    with open(MAPPING) as f:
        return yaml.safe_load(f) or {}


def load_techniques() -> dict:
    if not TECHNIQUES.exists():
        return {}
    return json.loads(TECHNIQUES.read_text())


def load_results() -> dict:
    if not RESULTS.exists():
        return {}
    return json.loads(RESULTS.read_text())


def save_results(data: dict):
    RESULTS.write_text(json.dumps(data, indent=2, default=str))


# ── Core API ──────────────────────────────────────────────────────────────────

def record_result(technique_id: str, module: str, status: str,
                  detected: bool, severity: Optional[str] = None,
                  details: Optional[dict] = None):
    """Called after each task completes to record detection result."""
    results = load_results()
    results[technique_id] = {
        "technique_id": technique_id,
        "module":       module,
        "status":       status,          # completed | failed
        "detected":     detected,        # did the SIEM/EDR catch it?
        "severity":     severity or "info",
        "details":      details or {},
        "timestamp":    datetime.utcnow().isoformat(),
    }
    save_results(results)


def get_coverage_summary() -> dict:
    """Full coverage summary across all tested techniques."""
    mapping    = load_mapping()
    techniques = load_techniques()
    results    = load_results()

    total_available = len(mapping)
    tested          = [tid for tid in mapping if tid in results]
    not_tested      = [tid for tid in mapping if tid not in results]

    by_tactic = {}
    for tid, config in mapping.items():
        tactic = config.get("tactic", "unknown")
        if tactic not in by_tactic:
            by_tactic[tactic] = {
                "tactic":     tactic,
                "color":      TACTIC_COLORS.get(tactic, "#94a3b8"),
                "total":      0,
                "tested":     0,
                "detected":   0,
                "not_tested": 0,
                "techniques": [],
            }

        result    = results.get(tid, {})
        is_tested = tid in results
        tech_info = techniques.get(tid, {})

        entry = {
            "id":       tid,
            "name":     config.get("name", tech_info.get("name", tid)),
            "module":   config.get("module"),
            "tool":     config.get("tool"),
            "tested":   is_tested,
            "detected": result.get("detected", False) if is_tested else None,
            "severity": result.get("severity")        if is_tested else None,
            "status":   result.get("status")          if is_tested else "pending",
        }

        by_tactic[tactic]["total"]      += 1
        by_tactic[tactic]["techniques"].append(entry)
        if is_tested:
            by_tactic[tactic]["tested"] += 1
        else:
            by_tactic[tactic]["not_tested"] += 1
        if result.get("detected"):
            by_tactic[tactic]["detected"] += 1

    # Order by kill chain
    ordered_tactics = {t: by_tactic[t] for t in TACTIC_ORDER if t in by_tactic}
    for t in by_tactic:
        if t not in ordered_tactics:
            ordered_tactics[t] = by_tactic[t]

    severity_counts = {}
    for r in results.values():
        sev = r.get("severity", "info")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "summary": {
            "total_techniques_mapped": total_available,
            "techniques_tested":       len(tested),
            "techniques_not_tested":   len(not_tested),
            "coverage_pct":            round(len(tested) / total_available * 100, 1) if total_available else 0,
            "detected_count":          sum(1 for r in results.values() if r.get("detected")),
            "severity_breakdown":      severity_counts,
        },
        "by_tactic":   ordered_tactics,
        "not_tested":  not_tested,
        "tested":      tested,
    }


def get_navigator_layer(campaign_name: str = "RedTeam Lab") -> dict:
    """
    Export ATT&CK Navigator layer JSON.
    Import at https://mitre-attack.github.io/attack-navigator/
    """
    results    = load_results()
    techniques_layer = []

    for tid, result in results.items():
        sev   = result.get("severity", "info")
        score = SEVERITY_SCORE.get(sev, 0)
        color = {
            "critical": "#dc2626",
            "high":     "#f97316",
            "medium":   "#eab308",
            "low":      "#22c55e",
            "info":     "#94a3b8",
        }.get(sev, "#94a3b8")

        techniques_layer.append({
            "techniqueID": tid,
            "score":       score,
            "color":       color if not result.get("detected") else "#16a34a",
            "comment":     f"Module: {result.get('module')} | Detected: {result.get('detected')} | Severity: {sev}",
            "enabled":     True,
            "metadata":    [],
        })

    return {
        "name":        campaign_name,
        "versions":    {"attack": "14", "navigator": "4.9", "layer": "4.5"},
        "domain":      "enterprise-attack",
        "description": f"RedTeam Lab coverage - {datetime.utcnow().strftime('%Y-%m-%d')}",
        "filters":     {"platforms": ["Linux", "macOS", "Windows"]},
        "sorting":     0,
        "layout":      {"layout": "side", "aggregateFunction": "max", "showID": True, "showName": True},
        "hideDisabled": False,
        "techniques":  techniques_layer,
        "gradient":    {"colors": ["#ffffff", "#ff6666"], "minValue": 0, "maxValue": 4},
        "legendItems": [
            {"label": "Critical",  "color": "#dc2626"},
            {"label": "High",      "color": "#f97316"},
            {"label": "Medium",    "color": "#eab308"},
            {"label": "Low",       "color": "#22c55e"},
            {"label": "Detected",  "color": "#16a34a"},
        ],
        "metadata":    [],
        "links":       [],
        "showTacticRowBackground": True,
        "tacticRowBackground": "#1e293b",
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False,
    }


def get_technique_plan(target: str) -> list:
    """
    Returns ordered list of all mapped techniques to execute against a target.
    Replaces {{target}} in params.
    """
    mapping = load_mapping()
    plan    = []

    for tid, config in mapping.items():
        params = {
            k: v.replace("{{target}}", target) if isinstance(v, str) else v
            for k, v in config.get("params", {}).items()
        }
        tactic = config.get("tactic", "unknown")
        plan.append({
            "mitre_id":       tid,
            "technique_name": config.get("name", tid),
            "module":         config.get("module"),
            "tool":           config.get("tool"),
            "tactic":         tactic,
            "tactic_order":   TACTIC_ORDER.index(tactic) if tactic in TACTIC_ORDER else 99,
            "params":         params,
        })

    plan.sort(key=lambda x: (x["tactic_order"], x["mitre_id"]))
    return plan


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MITRE ATT&CK Coverage Tool")
    sub    = parser.add_subparsers(dest="cmd")

    sub.add_parser("summary",   help="Print coverage summary")
    sub.add_parser("navigator", help="Export ATT&CK Navigator JSON layer")

    p_plan = sub.add_parser("plan", help="Show full attack plan for a target")
    p_plan.add_argument("target", help="IP or domain")

    p_record = sub.add_parser("record", help="Record a technique result")
    p_record.add_argument("technique_id")
    p_record.add_argument("module")
    p_record.add_argument("status", choices=["completed", "failed"])
    p_record.add_argument("--detected", action="store_true")
    p_record.add_argument("--severity", default="info")

    args = parser.parse_args()

    if args.cmd == "summary":
        data = get_coverage_summary()
        print(f"\n{'='*60}")
        print(f"  MITRE ATT&CK Coverage Summary")
        print(f"{'='*60}")
        s = data["summary"]
        print(f"  Techniques mapped:  {s['total_techniques_mapped']}")
        print(f"  Techniques tested:  {s['techniques_tested']}")
        print(f"  Coverage:           {s['coverage_pct']}%")
        print(f"  Detected by SIEM:   {s['detected_count']}")
        print(f"\n  By severity:")
        for sev, count in s["severity_breakdown"].items():
            print(f"    {sev:10s}: {count}")
        print(f"\n  By tactic:")
        for tactic, data in data["by_tactic"].items():
            pct = round(data['tested'] / data['total'] * 100) if data['total'] else 0
            print(f"    {tactic:30s}: {data['tested']:2d}/{data['total']:2d} ({pct}%)")
        print()

    elif args.cmd == "navigator":
        layer = get_navigator_layer()
        out   = BASE_DIR / "navigator_layer.json"
        out.write_text(json.dumps(layer, indent=2))
        print(f"Navigator layer saved to: {out}")
        print("Import at: https://mitre-attack.github.io/attack-navigator/")

    elif args.cmd == "plan":
        plan = get_technique_plan(args.target)
        print(f"\nAttack plan for {args.target} ({len(plan)} techniques):\n")
        current_tactic = ""
        for step in plan:
            if step["tactic"] != current_tactic:
                current_tactic = step["tactic"]
                print(f"\n  [{current_tactic.upper()}]")
            print(f"    {step['mitre_id']:12s} {step['technique_name']:45s} → {step['module']}")

    elif args.cmd == "record":
        record_result(args.technique_id, args.module, args.status,
                      args.detected, args.severity)
        print(f"Recorded: {args.technique_id} → {args.status} (detected={args.detected})")

    else:
        parser.print_help()
