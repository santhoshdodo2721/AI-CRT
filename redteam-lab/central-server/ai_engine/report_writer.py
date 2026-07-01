import logging
from sqlalchemy.orm import Session
from database.db import Campaign, Finding, Report
from ai_engine.llm_client import ask
from ai_engine.prompts import REPORTER_SYSTEM

logger = logging.getLogger("ai_engine.report_writer")

async def generate_campaign_report(db: Session, campaign_id: str) -> Report:
    """Generates a comprehensive Markdown report for a completed campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError("Campaign not found")
        
    findings = db.query(Finding).filter(Finding.campaign_id == campaign_id).all()
    
    findings_text = "\n".join(
        f"- [{f.severity.upper()}] {f.title}: {f.description} | MITRE: {f.mitre_id}"
        for f in findings
    ) or "No findings recorded."
    
    prompt = f"""
Campaign Name: {campaign.name}
Target: {campaign.target}

Findings:
{findings_text}

Please generate the final Executive and Technical Report.
"""
    
    report_md = await ask(prompt, system_prompt=REPORTER_SYSTEM, temperature=0.3, max_tokens=3000)
    
    report = Report(
        campaign_id=campaign_id,
        content=report_md,
        format="markdown"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report
