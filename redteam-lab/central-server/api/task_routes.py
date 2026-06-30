from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
import models
import json

router = APIRouter()

class AgentRegister(BaseModel):
    name: str

class TaskCreate(BaseModel):
    module: str
    target: str

class TaskSubmit(BaseModel):
    result: dict

@router.post("/agents/register")
def register_agent(data: AgentRegister, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.name == data.name).first()
    if not agent:
        agent = models.Agent(name=data.name)
        db.add(agent)
        db.commit()
        db.refresh(agent)
    return {"id": agent.id, "name": agent.name}

@router.post("/tasks/create")
def create_task(data: TaskCreate, db: Session = Depends(get_db)):
    task = models.Task(module=data.module, target=data.target)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id, "module": task.module, "target": task.target, "status": "pending"}

@router.get("/tasks/next")
def get_next_task(agent_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.status == "pending").first()
    if not task:
        return {"message": "No pending tasks"}
    task.status = "running"
    task.agent_id = agent_id
    db.commit()
    return {"id": task.id, "module": task.module, "target": task.target}

@router.post("/tasks/{task_id}/submit")
def submit_result(task_id: int, data: TaskSubmit, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "completed"
    task.result = json.dumps(data.result)
    db.commit()
    return {"status": "success"}

@router.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return [{"id": t.id, "module": t.module, "target": t.target, "status": t.status, "result": t.result} for t in tasks]