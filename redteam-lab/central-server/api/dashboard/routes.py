from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db, Campaign, Task, Finding
from api.auth.utils import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), _=Depends(get_current_user)):
    # Total Campaigns
    total_campaigns = db.query(Campaign).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "running").count()

    # Total Findings by Severity
    severity_counts = db.query(Finding.severity, func.count(Finding.id)).group_by(Finding.severity).all()
    # Normalize to a dict
    severity_dict = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }
    for sev, count in severity_counts:
        sev_lower = sev.lower()
        if sev_lower in severity_dict:
            severity_dict[sev_lower] = count
        else:
            severity_dict["info"] += count

    # Top MITRE Techniques
    # Extract mitre_id strings, split by comma, count
    findings = db.query(Finding.mitre_id).filter(Finding.mitre_id != "").all()
    mitre_counts = {}
    for (m_ids,) in findings:
        for m_id in m_ids.split(","):
            m = m_id.strip()
            if m and m != "None":
                mitre_counts[m] = mitre_counts.get(m, 0) + 1
    
    # Sort top 5
    top_mitre = sorted(mitre_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "campaigns": {
            "total": total_campaigns,
            "active": active_campaigns
        },
        "findings": {
            "total": sum(severity_dict.values()),
            "severity": severity_dict
        },
        "top_mitre": [{"id": m[0], "count": m[1]} for m in top_mitre]
    }
