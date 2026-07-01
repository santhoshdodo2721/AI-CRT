from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database.db import get_db, Task, Campaign, HostMemory, Finding
from pydantic import BaseModel
import datetime

router = APIRouter()

class SubmitResult(BaseModel):
    result: dict

@router.get("/next")
def get_next_task(db: Session = Depends(get_db)):
    """Agent polls this endpoint to get the next pending task."""
    task = db.query(Task).filter(Task.status == "pending").first()
    if not task:
        raise HTTPException(status_code=404, detail="No pending tasks")
    
    # Mark it as running
    task.status = "running"
    db.commit()
    
    return {
        "id": task.id,
        "campaign_id": task.campaign_id,
        "module": task.module,
        "params": task.params,
        "target": task.params.get("target", "127.0.0.1")  # Agent needs a target
    }

@router.post("/{task_id}/submit")
def submit_task_result(task_id: str, payload: SubmitResult, db: Session = Depends(get_db)):
    """Agent submits the result of a module execution."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result = payload.result
    task.result = result
    task.status = "completed"
    task.completed_at = datetime.datetime.utcnow()
    
    target = task.params.get("target")

    # Update host memory for nmap
    if task.module == "recon.nmap_scan" and "open_ports" in result and target:
        host_mem = db.query(HostMemory).filter(
            HostMemory.campaign_id == task.campaign_id,
            HostMemory.ip_address == target
        ).first()
        
        if not host_mem:
            host_mem = HostMemory(
                campaign_id=task.campaign_id,
                ip_address=target,
                open_ports=result["open_ports"],
                state={"last_scan": "nmap"}
            )
            db.add(host_mem)
        else:
            host_mem.open_ports = result["open_ports"]
            host_mem.state["last_scan"] = "nmap"

    # Add findings
    if "vulns" in result:
        for vuln in result["vulns"]:
            finding = Finding(
                campaign_id=task.campaign_id,
                task_id=task.id,
                title=vuln.get("title", "Discovered Vulnerability"),
                description=vuln.get("description", str(vuln)),
                severity=vuln.get("severity", "medium"),
                mitre_id=task.mitre_id or vuln.get("mitre_id", ""),
                raw_output=str(vuln)
            )
            db.add(finding)

    db.commit()
    return {"status": "ok"}
