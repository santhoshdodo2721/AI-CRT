from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict
from database.db import get_db, Campaign, Task, Finding
from api.auth.utils import get_current_user, require_role

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    target: str
    description: str = ""
    credentials: List[Dict[str, str]] = []
    scope_config: Dict[str, str] = {}
    ai_enabled: bool = True


@router.post("/", response_model=dict)
def create_campaign(camp: CampaignCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_camp = Campaign(
        name=camp.name,
        target=camp.target,
        description=camp.description,
        created_by=current_user.id,
        credentials=camp.credentials,
        scope_config=camp.scope_config,
        ai_enabled=camp.ai_enabled
    )
    db.add(new_camp)
    db.commit()
    db.refresh(new_camp)
    return {"message": "Campaign created", "id": new_camp.id}


@router.get("/")
def list_campaigns(db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaigns = db.query(Campaign).all()
    return [{"id": c.id, "name": c.name, "target": c.target, "status": c.status, "description": c.description} for c in campaigns]


@router.get("/findings/all")
def get_all_findings(db: Session = Depends(get_db), _=Depends(get_current_user)):
    findings = db.query(Finding).all()
    return [
        {
            "id": f.id,
            "campaign_id": f.campaign_id,
            "title": f.title,
            "severity": f.severity,
            "mitre_id": f.mitre_id,
            "created_at": f.created_at
        }
        for f in findings
    ]


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    from mitre.sync_mitre import get_mitre_for_module
    tasks = db.query(Task).filter(Task.campaign_id == campaign_id).all()
    findings = db.query(Finding).filter(Finding.campaign_id == campaign_id).all()
    return {
        "id": c.id, "name": c.name, "target": c.target, "status": c.status,
        "tasks": [{"id": t.id, "module": t.module, "status": t.status, "severity": t.severity, "mitre": get_mitre_for_module(t.module)} for t in tasks],
        "findings_count": len(findings),
    }


@router.post("/{campaign_id}/start")
def start_campaign(campaign_id: str, db: Session = Depends(get_db), _=Depends(require_role("admin", "operator"))):
    """Auto-create the standard recon → vuln → MITRE task chain."""
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")

    default_tasks = [
        {"module": "recon.nmap_scan",        "params": {"target": c.target, "ports": "1-65535", "flags": "-sV -sC"}},
        {"module": "recon.subdomain_scan",   "params": {"domain": c.target}},
        {"module": "recon.http_probe",       "params": {"target": c.target}},
        {"module": "recon.dirb_scan",        "params": {"target": c.target}},
        {"module": "vuln_scan.nuclei_scan",  "params": {"target": c.target}},
        {"module": "vuln_scan.sql_inject",   "params": {"target": c.target}},
        {"module": "vuln_scan.zap_scan",     "params": {"target": c.target}},
        {"module": "vuln_scan.trivy_scan",   "params": {"target": c.target}},
        {"module": "vuln_scan.semgrep_scan", "params": {"target": c.target}},
        {"module": "vuln_scan.gitleaks_scan","params": {"target": c.target}},
        {"module": "credentials.env_secret_scan", "params": {}},
    ]

    created = []
    for t in default_tasks:
        task = Task(campaign_id=campaign_id, module=t["module"], params=t["params"])
        db.add(task)
        created.append(t["module"])

    c.status = "running"
    db.commit()
    return {"started": True, "tasks_queued": created}

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str, db: Session = Depends(get_db), _=Depends(require_role("admin", "operator"))):
    c = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Manual cascading delete
    from database.db import Report, HostMemory, CredentialStore, AIDecisionLog, CampaignMemory, ToolExecution
    db.query(Finding).filter(Finding.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(Task).filter(Task.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(Report).filter(Report.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(HostMemory).filter(HostMemory.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(CredentialStore).filter(CredentialStore.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(AIDecisionLog).filter(AIDecisionLog.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(CampaignMemory).filter(CampaignMemory.campaign_id == campaign_id).delete(synchronize_session=False)
    db.query(ToolExecution).filter(ToolExecution.campaign_id == campaign_id).delete(synchronize_session=False)
    
    db.delete(c)
    db.commit()
    return {"status": "deleted", "id": campaign_id}

