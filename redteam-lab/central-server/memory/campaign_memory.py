import logging
from sqlalchemy.orm import Session
from database.db import CampaignMemory

logger = logging.getLogger("memory.campaign")

def get_campaign_memory(db: Session, campaign_id: str) -> dict:
    """Retrieve the high-level campaign memory state."""
    memory = db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).first()
    if not memory:
        return {}
    
    return {
        "phase": memory.phase,
        "completion_pct": memory.completion_pct,
        "risk_score": memory.risk_score,
        "global_state": memory.global_state
    }

def update_campaign_memory(db: Session, campaign_id: str, updates: dict):
    """Update specific fields in campaign memory."""
    memory = db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).first()
    if not memory:
        memory = CampaignMemory(campaign_id=campaign_id)
        db.add(memory)
        
    if "phase" in updates:
        memory.phase = updates["phase"]
    if "completion_pct" in updates:
        memory.completion_pct = updates["completion_pct"]
    if "risk_score" in updates:
        memory.risk_score = updates["risk_score"]
    if "global_state" in updates:
        current_state = memory.global_state or {}
        current_state.update(updates["global_state"])
        memory.global_state = current_state
        
    db.commit()
