"""
AI Auto-Attack Planner
Reads recon/scan results → maps to MITRE ATT&CK → generates attack plan → queues tasks
"""
import json
import os
import httpx
from pathlib import Path

OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

TECHNIQUES_FILE = Path(__file__).parent.parent / "mitre" / "techniques.json"

# All available modules mapped to MITRE technique IDs
MITRE_MODULE_MAP = {
    # Recon / Discovery
    "T1046":     "recon.nmap_scan",
    "T1595":     "recon.subdomain_scan",
    "T1190":     "vuln_scan.nuclei_scan",
    "T1592":     "recon.http_probe",
    "T1018":     "lateral_movement.network_reachability",

    # Initial Access
    "T1078":     "initial_access.default_creds_check",
    "T1133":     "initial_access.exposed_admin_check",
    "T1203":     "initial_access.known_cve_check",

    # Execution
    "T1059":     "execution.command_test",
    "T1059.003": "execution.atomic_runner",

    # Persistence
    "T1053":     "persistence.cron_test",
    "T1053.003": "persistence.cron_test",
    "T1543":     "persistence.systemd_test",

    # Privilege Escalation
    "T1548":     "privilege_escalation.sudo_check",
    "T1548.001": "privilege_escalation.suid_check",
    "T1574":     "privilege_escalation.writable_path_check",

    # Defense Evasion
    "T1027":     "defense_evasion.encoded_command_test",
    "T1070":     "defense_evasion.detection_check",

    # Credential Access
    "T1552":     "credentials.env_secret_scan",
    "T1552.001": "credentials.config_secret_scan",
    "T1213":     "credentials.repo_secret_scan",

    # Lateral Movement
    "T1021":     "lateral_movement.network_reachability",
    "T1021.004": "lateral_movement.ssh_check",

    # Exfiltration
    "T1048":     "exfiltration.egress_test",
    "T1041":     "exfiltration.dlp_check",

    # Impact
    "T1496":     "impact.cpu_load_test",
}

# Full attack chain ordered by MITRE tactic phase
TACTIC_ORDER = [
    "reconnaissance",
    "resource-development",
    "initial-access",
    "execution",
    "persistence",
    "privilege-escalation",
    "defense-evasion",
    "credential-access",
    "discovery",
    "lateral-movement",
    "collection",
    "command-and-control",
    "exfiltration",
    "impact",
]


def load_techniques() -> dict:
    if TECHNIQUES_FILE.exists():
        return json.loads(TECHNIQUES_FILE.read_text())
    return {}


async def ask_ollama(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=180) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json().get("response", "")
    except Exception as e:
        return f'{{"error": "{e}"}}'


async def generate_attack_plan(recon_results: dict, target: str) -> dict:
    """
    Given recon results, ask AI to generate a prioritized MITRE-mapped attack plan.
    Returns list of {mitre_id, technique_name, module, reason, params, priority}
    """
    techniques = load_techniques()

    # Build context from recon
    open_ports   = recon_results.get("open_ports", [])
    services     = [f"{p['port']}/{p.get('service','?')} ({p.get('product','')} {p.get('version','')})"
                    for p in open_ports]
    subdomains   = recon_results.get("subdomains", [])
    web_apps     = recon_results.get("web_apps", [])
    vuln_summary = recon_results.get("vuln_summary", "")

    prompt = f"""You are an expert red team operator planning a full attack simulation against a lab network.
Target: {target}

RECON RESULTS:
Open ports/services: {json.dumps(services[:30], indent=2)}
Subdomains found: {json.dumps(subdomains[:20], indent=2)}
Web applications: {json.dumps(web_apps[:10], indent=2)}
Vulnerability summary: {vuln_summary}

Available MITRE technique IDs and their modules:
{json.dumps(list(MITRE_MODULE_MAP.keys()), indent=2)}

Based on the recon results, generate a prioritized attack plan.
For each step, pick the most relevant MITRE technique ID from the list above.

Return ONLY a JSON array with no other text, like this:
[
  {{
    "mitre_id": "T1078",
    "reason": "Port 22 open with SSH - check for default/weak credentials",
    "priority": 1,
    "params": {{"target": "{target}"}}
  }},
  {{
    "mitre_id": "T1552",
    "reason": "Scan for exposed secrets in environment and config files",
    "priority": 2,
    "params": {{}}
  }}
]

Include all relevant techniques. Order by priority (1=highest). Return only JSON."""

    response = await ask_ollama(prompt)

    # Parse AI response
    try:
        clean = response.strip()
        # Find JSON array in response
        start = clean.find("[")
        end   = clean.rfind("]") + 1
        if start != -1 and end > start:
            clean = clean[start:end]
        plan_raw = json.loads(clean)
    except Exception:
        # Fallback: run the full default chain if AI parsing fails
        plan_raw = _default_full_chain(target)

    # Enrich with technique names and module names
    plan = []
    for step in plan_raw:
        tid    = step.get("mitre_id", "")
        module = MITRE_MODULE_MAP.get(tid)
        if not module:
            continue
        tech_info = techniques.get(tid, {})
        plan.append({
            "mitre_id":       tid,
            "technique_name": tech_info.get("name", tid),
            "tactic":         tech_info.get("tactic", []),
            "module":         module,
            "reason":         step.get("reason", ""),
            "priority":       step.get("priority", 99),
            "params":         step.get("params", {}),
        })

    # Sort by priority
    plan.sort(key=lambda x: x["priority"])
    return {"plan": plan, "total_steps": len(plan)}


def _default_full_chain(target: str) -> list:
    """Full attack chain used as fallback if AI parsing fails."""
    return [
        {"mitre_id": "T1046",     "priority": 1,  "reason": "Port scan to discover services", "params": {"target": target, "ports": "1-65535", "flags": "-sV -sC"}},
        {"mitre_id": "T1595",     "priority": 2,  "reason": "Subdomain enumeration", "params": {"domain": target}},
        {"mitre_id": "T1592",     "priority": 3,  "reason": "Web app fingerprinting", "params": {"target": target}},
        {"mitre_id": "T1190",     "priority": 4,  "reason": "Vulnerability scan", "params": {"target": target}},
        {"mitre_id": "T1078",     "priority": 5,  "reason": "Default credential check", "params": {"target": target}},
        {"mitre_id": "T1133",     "priority": 6,  "reason": "Exposed admin panel check", "params": {"target": target}},
        {"mitre_id": "T1203",     "priority": 7,  "reason": "Known CVE check", "params": {"target": target}},
        {"mitre_id": "T1059",     "priority": 8,  "reason": "Command execution test", "params": {}},
        {"mitre_id": "T1053.003", "priority": 9,  "reason": "Cron persistence simulation", "params": {}},
        {"mitre_id": "T1543",     "priority": 10, "reason": "Systemd persistence simulation", "params": {}},
        {"mitre_id": "T1548",     "priority": 11, "reason": "Sudo misconfiguration check", "params": {}},
        {"mitre_id": "T1548.001", "priority": 12, "reason": "SUID binary check", "params": {}},
        {"mitre_id": "T1574",     "priority": 13, "reason": "Writable PATH check", "params": {}},
        {"mitre_id": "T1027",     "priority": 14, "reason": "Encoded command evasion test", "params": {}},
        {"mitre_id": "T1070",     "priority": 15, "reason": "Detection evasion check", "params": {}},
        {"mitre_id": "T1552",     "priority": 16, "reason": "Environment secret scan", "params": {}},
        {"mitre_id": "T1552.001", "priority": 17, "reason": "Config file secret scan", "params": {}},
        {"mitre_id": "T1213",     "priority": 18, "reason": "Repo secret scan", "params": {}},
        {"mitre_id": "T1021",     "priority": 19, "reason": "Network reachability mapping", "params": {"network": target}},
        {"mitre_id": "T1021.004", "priority": 20, "reason": "SSH lateral movement check", "params": {"target": target}},
        {"mitre_id": "T1048",     "priority": 21, "reason": "Egress/exfiltration test", "params": {}},
        {"mitre_id": "T1041",     "priority": 22, "reason": "DLP effectiveness check", "params": {}},
        {"mitre_id": "T1496",     "priority": 23, "reason": "Resource impact simulation", "params": {}},
    ]
