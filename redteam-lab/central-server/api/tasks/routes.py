from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db, Task, Finding
from api.auth.utils import get_current_user, require_role

router = APIRouter()

ALLOWED_MODULES = {
    "recon.nmap_scan", "recon.subdomain_scan", "recon.http_probe", "recon.service_detect",
    "vuln_scan.nuclei_scan", "vuln_scan.zap_scan", "vuln_scan.trivy_scan",
    "initial_access.default_creds_check", "initial_access.exposed_admin_check",
    "initial_access.known_cve_check",
    "execution.atomic_runner", "execution.command_test",
    "persistence.cron_test", "persistence.systemd_test",
    "privilege_escalation.sudo_check", "privilege_escalation.suid_check",
    "privilege_escalation.writable_path_check",
    "defense_evasion.encoded_command_test", "defense_evasion.detection_check",
    "credentials.env_secret_scan", "credentials.config_secret_scan", "credentials.repo_secret_scan",
    "lateral_movement.network_reachability", "lateral_movement.ssh_check",
    "exfiltration.egress_test", "exfiltration.dlp_check",
    "impact.cpu_load_test",
}


class TaskCreate(BaseModel):
    campaign_id: str
    module:      str
    params:      dict = {}
    mitre_id:    Optional[str] = None


@router.post("/")
def create_task(req: TaskCreate, db: Session = Depends(get_db), _=Depends(require_role("admin", "operator"))):
    if req.module not in ALLOWED_MODULES:
        raise HTTPException(status_code=400, detail=f"Module '{req.module}' is not in the allowlist.")
    task = Task(campaign_id=req.campaign_id, module=req.module, params=req.params, mitre_id=req.mitre_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return {"id": task.id, "module": task.module, "status": task.status}


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id":           task.id,
        "campaign_id":  task.campaign_id,
        "module":       task.module,
        "params":       task.params,
        "status":       task.status,
        "result":       task.result,
        "mitre_id":     task.mitre_id,
        "severity":     task.severity,
        "created_at":   task.created_at,
        "completed_at": task.completed_at,
    }


@router.get("/campaign/{campaign_id}")
def get_campaign_tasks(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    tasks = db.query(Task).filter(Task.campaign_id == campaign_id).all()
    return [{"id": t.id, "module": t.module, "status": t.status, "severity": t.severity} for t in tasks]
