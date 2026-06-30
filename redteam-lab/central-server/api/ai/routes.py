from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os, httpx
from database.db import get_db, Task, Finding, Campaign
from api.auth.utils import get_current_user

router = APIRouter()

OLLAMA_URL  = os.getenv("OLLAMA_URL",  "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")


async def ask_ai_model(prompt: str) -> str:
    """Call NVIDIA NIM API if key exists, else fallback to local Ollama."""
    if NVIDIA_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {NVIDIA_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta/llama-3.1-8b-instruct",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "top_p": 0.7,
                        "max_tokens": 1024,
                        "stream": False
                    },
                )
                r.raise_for_status()
                data = r.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"NVIDIA NIM API Error: {e}. Falling back to Ollama...")
            pass # Fall through to local Ollama
    
    # Fallback to local Ollama
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json().get("response", "")
    except Exception as e:
        return f"[AI offline – run Ollama locally] Error: {e}"


class AskRequest(BaseModel):
    question: str
    context:  str = ""


@router.post("/ask")
async def ask_ai(req: AskRequest, _=Depends(get_current_user)):
    system = (
        "You are a red-team security analyst assistant. "
        "Provide concise, actionable analysis. Map findings to MITRE ATT&CK where relevant. "
        "Suggest concrete remediation steps. Never recommend illegal activity."
    )
    prompt = f"{system}\n\nContext:\n{req.context}\n\nQuestion: {req.question}"
    answer = await ask_ai_model(prompt)
    return {"answer": answer}


@router.post("/analyze-task/{task_id}")
async def analyze_task(task_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task or not task.result:
        raise HTTPException(status_code=404, detail="Task or result not found")

    from mitre.sync_mitre import get_mitre_for_module
    mitre_info = get_mitre_for_module(task.module)

    prompt = (
        f"Analyze this red-team task result.\n"
        f"Module: {task.module}\n"
        f"Mapped MITRE Technique: {mitre_info.get('id')} - {mitre_info.get('name')}\n"
        f"Parameters: {task.params}\n"
        f"Raw output:\n{task.result}\n\n"
        "Provide:\n"
        "1. Summary of findings\n"
        "2. MITRE ATT&CK technique IDs if applicable\n"
        "3. Severity (critical/high/medium/low/info)\n"
        "4. Recommended remediation\n"
        "Return as JSON with keys: summary, mitre_ids, severity, remediation"
    )
    answer = await ask_ai_model(prompt)

    # Try to parse and persist as a Finding
    try:
        import json
        clean = answer.strip().lstrip("```json").rstrip("```").strip()
        data  = json.loads(clean)
        finding = Finding(
            campaign_id=task.campaign_id,
            task_id=task.id,
            title=f"[{task.module}] AI Analysis",
            description=data.get("summary", ""),
            severity=data.get("severity", "info"),
            mitre_id=", ".join(data.get("mitre_ids", [])),
            remediation=data.get("remediation", ""),
        )
        db.add(finding)
        task.severity = data.get("severity", "info")
        db.commit()
    except Exception:
        pass   # raw answer still returned

    return {"analysis": answer}


@router.post("/generate-report/{campaign_id}")
async def generate_report(campaign_id: str, db: Session = Depends(get_db), _=Depends(get_current_user)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    findings = db.query(Finding).filter(Finding.campaign_id == campaign_id).all()
    findings_text = "\n".join(
        f"- [{f.severity.upper()}] {f.title}: {f.description} | Remediation: {f.remediation}"
        for f in findings
    ) or "No findings recorded yet."

    prompt = (
        f"Write a highly detailed, professional red-team engagement report for:\n"
        f"Campaign: {campaign.name}\n"
        f"Target: {campaign.target}\n\n"
        f"Findings:\n{findings_text}\n\n"
        "Please provide a comprehensive and detailed analysis.\n"
        "Include: Executive Summary, Findings Table, Attack Path, MITRE ATT&CK Coverage, and Remediation Roadmap.\n"
        "Format the entire report using clear Markdown (use ## for headers, bold text for emphasis, and proper Markdown tables)."
    )
    report_md = await ask_ai_model(prompt)
    return {"campaign": campaign.name, "report": report_md}
