from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime
from database.db import get_db, Agent, Task
from api.auth.utils import get_current_user

router = APIRouter()

# ── Agent self-registration (called by the agent binary) ──────────────────────

class AgentRegisterRequest(BaseModel):
    name: str
    hostname: str
    ip_address: str
    os_info: str

@router.post("/register")
def register_agent(req: AgentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Agent).filter(Agent.hostname == req.hostname).first()
    if existing:
        existing.ip_address = req.ip_address
        existing.os_info    = req.os_info
        existing.status     = "online"
        existing.last_seen  = datetime.datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return {"agent_id": existing.id, "status": "updated"}

    agent = Agent(
        name=req.name,
        hostname=req.hostname,
        ip_address=req.ip_address,
        os_info=req.os_info,
        status="online",
        last_seen=datetime.datetime.utcnow(),
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"agent_id": agent.id, "status": "registered"}


# ── Heartbeat ─────────────────────────────────────────────────────────────────

class HeartbeatRequest(BaseModel):
    agent_id: str
    status: str = "idle"

@router.post("/heartbeat")
def heartbeat(req: HeartbeatRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == req.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.last_seen = datetime.datetime.utcnow()
    agent.status    = req.status
    db.commit()
    return {"ok": True}


# ── Task polling (agent asks for next pending task) ───────────────────────────

@router.get("/tasks/next/{agent_id}")
def get_next_task(agent_id: str, db: Session = Depends(get_db)):
    task = (
        db.query(Task)
        .filter(Task.status == "pending", Task.agent_id.is_(None))
        .order_by(Task.created_at)
        .first()
    )
    if not task:
        return {"task": None}
    task.agent_id = agent_id
    task.status   = "assigned"
    db.commit()
    db.refresh(task)
    return {
        "task": {
            "id":     task.id,
            "module": task.module,
            "params": task.params,
        }
    }


# ── Result submission ─────────────────────────────────────────────────────────

class TaskResultRequest(BaseModel):
    task_id:  str
    agent_id: str
    status:   str        # "completed" | "failed"
    result:   dict

@router.post("/tasks/result")
def submit_result(req: TaskResultRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == req.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status       = req.status
    task.result       = req.result
    task.completed_at = datetime.datetime.utcnow()
    db.commit()
    return {"ok": True}


# ── Management endpoints (requires login) ────────────────────────────────────

@router.get("/")
def list_agents(db: Session = Depends(get_db), _=Depends(get_current_user)):
    agents = db.query(Agent).all()
    return [
        {
            "id":          a.id,
            "name":        a.name,
            "hostname":    a.hostname,
            "ip_address":  a.ip_address,
            "os_info":     a.os_info,
            "status":      a.status,
            "last_seen":   a.last_seen,
        }
        for a in agents
    ]
