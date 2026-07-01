import json
import logging
from sqlalchemy.orm import Session
from database.db import Campaign, HostMemory, Finding
from ai_engine.llm_client import ask_json
from ai_engine.prompts import ANALYZER_SYSTEM

logger = logging.getLogger("ai_engine.analyzer")

async def analyze_tool_output(db: Session, campaign_id: str, task_id: str, tool_name: str, raw_output: str, target_ip: str = None) -> dict:
    """Analyzes raw tool output and updates state/findings."""
    
    prompt = f"""
Tool Name: {tool_name}
Target IP: {target_ip}

Raw Output:
{raw_output}
"""
    
    analysis = await ask_json(prompt, system_prompt=ANALYZER_SYSTEM)
    
    if analysis:
        # Create Finding records
        for finding_text in analysis.get("findings", []):
            finding = Finding(
                campaign_id=campaign_id,
                task_id=task_id,
                title=f"[{tool_name}] Finding",
                description=finding_text,
                severity=analysis.get("severity", "info"),
                mitre_id=",".join(analysis.get("mitre_ids", [])),
                raw_output=raw_output[:1000] # store snippet
            )
            db.add(finding)
            
        # Update Host Memory
        new_state = analysis.get("new_state", {})
        if target_ip and new_state:
            host = db.query(HostMemory).filter(HostMemory.campaign_id == campaign_id, HostMemory.ip_address == target_ip).first()
            if not host:
                host = HostMemory(campaign_id=campaign_id, ip_address=target_ip)
                db.add(host)
            
            # Merge state
            if "open_ports" in new_state:
                current_ports = set(host.open_ports or [])
                current_ports.update(new_state["open_ports"])
                host.open_ports = list(current_ports)
                
            if "services" in new_state:
                current_services = host.services or {}
                current_services.update(new_state["services"])
                host.services = current_services
                
        db.commit()
        
    return analysis
