from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from database.db import get_db, Finding, Campaign
from api.auth.utils import get_current_user

router = APIRouter()


@router.get("/{campaign_id}")
def get_findings(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    findings = db.query(Finding).filter(Finding.campaign_id == campaign_id).all()
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings_sorted = sorted(findings, key=lambda f: severity_order.get(f.severity, 5))

    return {
        "campaign": campaign.name,
        "target":   campaign.target,
        "findings": [
            {
                "id":          f.id,
                "title":       f.title,
                "severity":    f.severity,
                "mitre_id":    f.mitre_id,
                "description": f.description,
                "remediation": f.remediation,
                "created_at":  f.created_at,
            }
            for f in findings_sorted
        ],
        "summary": {
            "total":    len(findings),
            "critical": sum(1 for f in findings if f.severity == "critical"),
            "high":     sum(1 for f in findings if f.severity == "high"),
            "medium":   sum(1 for f in findings if f.severity == "medium"),
            "low":      sum(1 for f in findings if f.severity == "low"),
        }
    }
