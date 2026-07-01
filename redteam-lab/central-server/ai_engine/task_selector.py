import json
import logging
from sqlalchemy.orm import Session
from database.db import Campaign, CampaignMemory, HostMemory, Task
from ai_engine.llm_client import ask_json
from ai_engine.prompts import TASK_SELECTOR_SYSTEM

logger = logging.getLogger("ai_engine.task_selector")

async def select_next_task(db: Session, campaign_id: str) -> dict:
    """Uses the LLM to decide the exact next action based on current state."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return {"error": "Campaign not found"}
        
    memory = db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).first()
    hosts = db.query(HostMemory).filter(HostMemory.campaign_id == campaign_id).all()
    tasks = db.query(Task).filter(Task.campaign_id == campaign_id).all()
    
    hosts_data = []
    for h in hosts:
        hosts_data.append({
            "ip": h.ip_address,
            "open_ports": h.open_ports,
            "services": h.services,
            "vulns": h.vulns
        })
        
    active_tasks = [t.module for t in tasks if t.status in ["pending", "running"]]
    completed_tasks = [t.module for t in tasks if t.status == "completed"][-5:]
    
    state_summary = {
        "target": campaign.target,
        "phase": memory.phase if memory else "recon",
        "hosts": hosts_data,
        "active_tasks_in_queue": active_tasks,
        "recently_completed_tasks": completed_tasks,
        "credentials_provided": bool(campaign.credentials)
    }
    
    prompt = f"Current Environment State:\n{json.dumps(state_summary, indent=2)}\n\nWhat is the exact next action to take?"
    
    decision = await ask_json(prompt, system_prompt=TASK_SELECTOR_SYSTEM)
    return decision or {"action": "wait", "reasoning": "Fallback due to LLM failure"}
