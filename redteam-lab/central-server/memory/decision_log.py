import logging
from sqlalchemy.orm import Session
from database.db import AIDecisionLog

logger = logging.getLogger("memory.decision")

def get_recent_decisions(db: Session, campaign_id: str, limit: int = 10) -> list:
    """Returns the most recent AI decisions for the dashboard."""
    logs = db.query(AIDecisionLog).filter(
        AIDecisionLog.campaign_id == campaign_id
    ).order_by(AIDecisionLog.step.desc()).limit(limit).all()
    
    return [
        {
            "type": "ai.thought",
            "step": log.step,
            "action": log.action,
            "tool": log.tool_name,
            "observation": log.state_summary,
            "reasoning": log.reasoning,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]
