import json
import logging
from typing import List
from ai_engine.llm_client import ask_json
from ai_engine.prompts import TOOL_SELECTOR_SYSTEM

logger = logging.getLogger("ai_engine.tool_selector")

# In a real system, this would be queried from the agent or a ToolManager registry
AVAILABLE_TOOLS = [
    {"name": "recon.nmap_scan", "description": "Port scanning and service detection", "category": "port_scan"},
    {"name": "recon.subdomain_scan", "description": "Subdomain enumeration", "category": "subdomain_enum"},
    {"name": "recon.http_probe", "description": "HTTP probe for active web servers", "category": "http_probe"},
    {"name": "vuln_scan.nuclei_scan", "description": "Web vulnerability scanner", "category": "web_vuln_scan"},
    {"name": "vuln_scan.sql_inject", "description": "SQL Injection tester", "category": "sql_inject"},
    {"name": "initial_access.netexec_smb", "description": "SMB authentication and share mapping", "category": "smb_auth_check"},
    {"name": "initial_access.exposed_admin_check", "description": "Check for exposed admin panels", "category": "admin_check"},
    {"name": "initial_access.brute_force_ssh", "description": "SSH brute force simulation", "category": "ssh_brute"},
    {"name": "execution.command_test", "description": "Simulate command execution", "category": "execution"},
    {"name": "persistence.cron_test", "description": "Simulate cron job persistence", "category": "persistence"},
    {"name": "privilege_escalation.sudo_check", "description": "Check for sudo misconfigurations", "category": "privilege_escalation"},
    {"name": "defense_evasion.detection_check", "description": "Check if defensive tools are running", "category": "defense_evasion"},
    {"name": "credentials.env_secret_scan", "description": "Scan environment variables for secrets", "category": "credential_access"},
    {"name": "lateral_movement.network_reachability", "description": "Check lateral movement paths", "category": "lateral_movement"},
    {"name": "exfiltration.dummy_file_create", "description": "Simulate data exfiltration via dummy file", "category": "exfiltration"},
    {"name": "impact.file_rename_test", "description": "Simulate ransomware file encryption/rename", "category": "impact"},
    {"name": "impact.cpu_load_test", "description": "Simulate cryptojacking CPU load", "category": "impact"}
]

async def select_tool_for_action(action: dict, available_tools: List[dict] = AVAILABLE_TOOLS) -> dict:
    """Uses the LLM to choose the best tool for the desired action."""
    
    prompt = f"""
Desired Action:
{json.dumps(action, indent=2)}

Available Tools:
{json.dumps(available_tools, indent=2)}

Select the most appropriate tool and define its parameters.
"""
    
    decision = await ask_json(prompt, system_prompt=TOOL_SELECTOR_SYSTEM)
    return decision or {"tool_name": None, "reasoning": "Fallback due to LLM failure"}
