import json
import logging
from sqlalchemy.orm import Session
from database.db import Campaign, CampaignMemory, HostMemory, CredentialStore
from ai_engine.llm_client import ask_json
from ai_engine.prompts import PLANNER_SYSTEM

logger = logging.getLogger("ai_engine.planner")

async def determine_next_phase(db: Session, campaign_id: str) -> dict:
    """Uses the LLM to determine the next phase of the campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return {"error": "Campaign not found"}
        
    memory = db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).first()
    hosts = db.query(HostMemory).filter(HostMemory.campaign_id == campaign_id).all()
    
    current_phase = memory.phase if memory else "recon"
    
    state_summary = {
        "target": campaign.target,
        "current_phase": current_phase,
        "hosts_discovered": len(hosts),
        "known_ports": [h.open_ports for h in hosts],
        "scope": campaign.scope_config
    }
    
    prompt = f"Current Campaign State:\n{json.dumps(state_summary, indent=2)}\n\nWhat should be the next phase?"
    
    decision = await ask_json(prompt, system_prompt=PLANNER_SYSTEM)
    
    if decision:
        if memory and decision.get("next_phase") and decision.get("next_phase") != memory.phase:
            memory.phase = decision["next_phase"]
            db.commit()
            
    return decision or {"next_phase": current_phase, "is_complete": False, "reasoning": "Fallback to current phase"}
