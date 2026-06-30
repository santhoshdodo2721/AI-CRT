"""
Auto-Attack Planning Routes - uses mapping.yaml + coverage.py
POST /api/ai/auto-plan/{campaign_id}    → AI generates MITRE-mapped plan from recon
POST /api/ai/auto-execute/{campaign_id} → Queues all planned attack tasks (from mapping.yaml)
GET  /api/ai/coverage/{campaign_id}     → MITRE coverage per tactic
GET  /api/ai/navigator/{campaign_id}    → ATT&CK Navigator layer JSON
POST /api/ai/full-chain/{campaign_id}   → Queue EVERY technique from mapping.yaml
"""
import sys, os
# Server runs inside central-server/, project root is one level up
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database.db import get_db, Campaign, Task, Finding
from api.auth.utils import get_current_user, require_role
from ai_engine.planner import generate_attack_plan, load_techniques, TACTIC_ORDER
from mitre.coverage import (
    get_coverage_summary, get_navigator_layer, get_technique_plan,
    record_result, load_mapping
)
import datetime, json

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


def _gather_recon(campaign_id: str, db: Session) -> dict:
    recon_modules = {"recon.nmap_scan", "recon.subdomain_scan", "recon.http_probe", "vuln_scan.nuclei_scan"}
    tasks = db.query(Task).filter(
        Task.campaign_id == campaign_id,
        Task.module.in_(recon_modules),
        Task.status == "completed"
    ).all()
    recon = {"open_ports": [], "subdomains": [], "web_apps": [], "vuln_summary": ""}
    for t in tasks:
        if not t.result:
            continue
        if t.module == "recon.nmap_scan":
            recon["open_ports"] = t.result.get("open_ports", [])
        elif t.module == "recon.subdomain_scan":
            recon["subdomains"] = t.result.get("subdomains", [])
        elif t.module == "recon.http_probe":
            recon["web_apps"]   = t.result.get("results", [])
        elif t.module == "vuln_scan.nuclei_scan":
            findings = t.result.get("findings", [])
            recon["vuln_summary"] = f"{len(findings)} vuln findings"
    return recon


def _queue_steps(steps: list, campaign_id: str, target: str, db: Session) -> tuple:
    queued, skipped = [], []
    for step in steps:
        module = step.get("module")
        if not module or module not in ALLOWED_MODULES:
            skipped.append(step.get("module", "unknown"))
            continue
        params = step.get("params", {})
        if "target" not in params and target:
            params["target"] = target
        task = Task(
            campaign_id=campaign_id,
            module=module,
            params=params,
            mitre_id=step.get("mitre_id"),
        )
        db.add(task)
        queued.append({"module": module, "mitre_id": step.get("mitre_id"),
                        "tactic": step.get("tactic", ""), "reason": step.get("reason", "")})
    db.commit()
    return queued, skipped


# ── Route 1: AI plan (preview only, no queuing) ───────────────────────────────

@router.post("/auto-plan/{campaign_id}")
async def auto_plan(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    recon        = _gather_recon(campaign_id, db)
    plan_result  = await generate_attack_plan(recon, campaign.target)
    return {
        "campaign_id":   campaign_id,
        "target":        campaign.target,
        "recon_summary": {k: len(v) if isinstance(v, list) else v for k, v in recon.items()},
        "attack_plan":   plan_result["plan"],
        "total_steps":   plan_result["total_steps"],
        "note": "POST /api/ai/auto-execute/{id} to queue, or /api/ai/full-chain/{id} for ALL techniques",
    }


# ── Route 2: AI-selected execution ───────────────────────────────────────────

@router.post("/auto-execute/{campaign_id}")
async def auto_execute(campaign_id: str, db: Session = Depends(get_db),
                       _=Depends(require_role("admin", "operator"))):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")
    recon       = _gather_recon(campaign_id, db)
    plan_result = await generate_attack_plan(recon, campaign.target)
    queued, skipped = _queue_steps(plan_result["plan"], campaign_id, campaign.target, db)
    campaign.status = "running"
    db.commit()
    return {
        "campaign_id":    campaign_id,
        "tasks_queued":   len(queued),
        "tasks_skipped":  len(skipped),
        "execution_plan": queued,
    }


# ── Route 3: FULL chain from mapping.yaml (all techniques) ───────────────────

@router.post("/full-chain/{campaign_id}")
def full_chain(campaign_id: str, db: Session = Depends(get_db),
               _=Depends(require_role("admin", "operator"))):
    """
    Queues ALL techniques defined in mapping.yaml in kill-chain order.
    This is the complete MITRE ATT&CK simulation run.
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    plan = get_technique_plan(campaign.target)   # from mapping.yaml, target substituted
    queued, skipped = _queue_steps(plan, campaign_id, campaign.target, db)
    campaign.status = "running"
    db.commit()

    # Group queued by tactic for display
    by_tactic = {}
    for q in queued:
        t = q.get("tactic", "unknown")
        by_tactic.setdefault(t, []).append(q)

    return {
        "campaign_id":   campaign_id,
        "target":        campaign.target,
        "total_queued":  len(queued),
        "total_skipped": len(skipped),
        "skipped":       skipped,
        "by_tactic":     by_tactic,
        "message": f"Queued {len(queued)} MITRE-mapped tasks across {len(by_tactic)} tactics. Agent executing in order.",
    }


# ── Route 4: Coverage heatmap ─────────────────────────────────────────────────

@router.get("/coverage/{campaign_id}")
def mitre_coverage(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Sync DB task results into coverage_results.json
    tasks = db.query(Task).filter(Task.campaign_id == campaign_id,
                                   Task.status.in_(["completed", "failed"])).all()
    for task in tasks:
        if not task.mitre_id:
            continue
        for tid in task.mitre_id.split(","):
            tid = tid.strip()
            if tid:
                record_result(
                    technique_id=tid,
                    module=task.module,
                    status=task.status,
                    detected=False,      # updated by detection_check module
                    severity=task.severity or "info",
                    details={"task_id": task.id, "campaign_id": campaign_id},
                )

    data = get_coverage_summary()
    return {
        "campaign_id": campaign_id,
        "target":      campaign.target,
        **data,
    }


# ── Route 5: ATT&CK Navigator export ─────────────────────────────────────────

@router.get("/navigator/{campaign_id}")
def navigator_layer(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(404, "Campaign not found")

    # Sync results first
    tasks = db.query(Task).filter(Task.campaign_id == campaign_id,
                                   Task.status.in_(["completed", "failed"])).all()
    for task in tasks:
        if task.mitre_id:
            for tid in task.mitre_id.split(","):
                tid = tid.strip()
                if tid:
                    record_result(tid, task.module, task.status, False,
                                  task.severity or "info", {"task_id": task.id})

    layer = get_navigator_layer(campaign_name=campaign.name)
    return JSONResponse(content=layer, headers={
        "Content-Disposition": f'attachment; filename="navigator_{campaign_id[:8]}.json"'
    })


# ── Route 6: Mapping reference ───────────────────────────────────────────────

@router.get("/mapping")
def get_mapping(_=Depends(get_current_user)):
    """Returns the full technique → module mapping from mapping.yaml."""
    mapping    = load_mapping()
    techniques = load_techniques()
    result     = {}
    for tid, config in mapping.items():
        tech = techniques.get(tid, {})
        result[tid] = {
            **config,
            "mitre_url": f"https://attack.mitre.org/techniques/{tid.replace('.', '/')}",
            "description": tech.get("description", "")[:200],
        }
    return {"total": len(result), "mapping": result}
