from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.db import SessionLocal, Campaign
from ai_engine.orchestrator import run_campaign_loop
from ai_engine.report_writer import generate_campaign_report
from memory.decision_log import get_recent_decisions
from api.websocket.manager import manager
from pydantic import BaseModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/start-campaign/{campaign_id}")
async def start_campaign(campaign_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Starts the autonomous AI orchestrator loop for a campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    campaign.status = "running"
    db.commit()
    
    await manager.broadcast_to_campaign(campaign_id, {"type": "campaign.started", "campaign_id": campaign_id})
    
    # Launch orchestrator in background
    background_tasks.add_task(run_campaign_loop, campaign_id)
    
    return {"status": "started", "campaign_id": campaign_id}

@router.post("/stop-campaign/{campaign_id}")
async def stop_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """Pauses the AI orchestrator."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    campaign.status = "paused"
    db.commit()
    
    await manager.broadcast_to_campaign(campaign_id, {"type": "campaign.paused", "campaign_id": campaign_id})
    return {"status": "paused", "campaign_id": campaign_id}

@router.get("/thoughts/{campaign_id}")
async def get_ai_thoughts(campaign_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Retrieves the recent decision log of the AI."""
    decisions = get_recent_decisions(db, campaign_id, limit)
    return {"decisions": decisions}

@router.post("/generate-report/{campaign_id}")
async def generate_report(campaign_id: str, db: Session = Depends(get_db)):
    """Generates the final engagement report."""
    report = await generate_campaign_report(db, campaign_id)
    return {"status": "generated", "report_id": report.id}

class AskRequest(BaseModel):
    question: str
    context: str = ""

@router.post("/ask")
async def ask_ai(req: AskRequest, db: Session = Depends(get_db)):
    # Legacy endpoint kept for direct dashboard querying if needed
    from ai_engine.llm_client import ask
    answer = await ask(req.question, system_prompt=req.context)
    return {"answer": answer}
