from fastapi import APIRouter
from pydantic import BaseModel
import json
import requests as llm_req

router = APIRouter()
task_db = []
task_counter = 0

LLM_URL = "http://localhost:8001/v1/chat/completions" 
LLM_MODEL = "meta/llama3-8b-instruct" 

class TaskCreate(BaseModel):
    module: str
    target: str
    ports: str = "8000"

class TaskResult(BaseModel):
    result: dict

def ask_llama(raw_data: dict) -> dict:
    prompt = f"""You are an expert Red Team Operator and MITRE ATT&CK analyst. Analyze this raw security tool output and return a JSON object with these exact keys: "summary" (string), "risk_level" (string: Low, Medium, High, Critical), "findings" (array of strings), "mitre_techniques" (array of objects with "id" and "name"), "next_steps" (array of strings). Tool Output: {json.dumps(raw_data)}"""
    try:
        res = llm_req.post(LLM_URL, json={"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}, timeout=30)
        content = res.json()["choices"][0]["message"]["content"]
        if "```json" in content: content = content.split("```json")[1].split("```")[0]
        return json.loads(content)
    except Exception as e:
        print(f"[LLM ERROR]: {e}")
        return None

def analyze_results_fallback(module: str, target: str, result_data: dict) -> dict:
    report = {"target": target, "module_run": module, "findings": [], "mitre_techniques": [], "risk_level": "Info", "next_steps": [], "error": result_data.get("error")}

    if "recon" in module or "nmap" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1046"), "name": "Network Service Discovery"})
        ports = result_data.get("open_ports", [])
        if ports:
            report["risk_level"] = "Low"
            for p in ports: report["findings"].append(f"Open Port: {p['port']}/{p['protocol']} - {p['service']}")
            report["summary"] = f"Discovered {len(ports)} open port(s)."
            if any(p['service'] in ['http', 'https'] for p in ports): report["next_steps"].append("Run Vulnerability Scanner (Nuclei) against HTTP ports.")
        else: report["summary"] = "No open ports found."

    elif "vuln" in module or "nuclei" in module:
        report["mitre_techniques"].append({"id": "T1595.002", "name": "Active Scanning"})
        vulns = result_data.get("details", [])
        if vulns:
            report["risk_level"] = "Medium"
            report["summary"] = f"Found {len(vulns)} vulnerabilities."
            if any("swagger" in v.get("template_id", "").lower() for v in vulns): report["findings"].append("Exposed API Documentation.")
        else: report["summary"] = "No vulnerabilities found."
        
    elif "initial_access" in module or "creds" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1078.001"), "name": result_data.get("technique_name", "Default Accounts")})
        details = result_data.get("details", [])
        if details:
            report["risk_level"] = "Critical"
            report["summary"] = f"CRITICAL: Default credentials work!"
            for d in details: report["findings"].append(f"Valid Creds: {d.get('user', '?')}:{d.get('pass', '?')}")
            report["next_steps"].append("Immediate patch required.")
        else:
            report["risk_level"] = "Low"
            report["summary"] = "Default credentials check failed. System is secure."

    elif "execution" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1059.004"), "name": "Command and Scripting Interpreter"})
        details = result_data.get("details", [])
        if details:
            report["risk_level"] = "Info"
            report["summary"] = f"Execution simulation successful."
            for d in details:
                if d.get("success"): report["findings"].append(f"Executed '{d['command']}': {d.get('output', '')}")
        else: report["summary"] = "Execution test failed."

    elif "persistence" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1053.003"), "name": "Scheduled Task/Job: Cron"})
        report["risk_level"] = result_data.get("risk_level", "Info")
        report["summary"] = result_data.get("summary", "Persistence test completed.")
        details = result_data.get("details", [])
        if details and details[0].get("success"): report["findings"].append("Successfully installed and removed cron job.")

    elif "privilege_escalation" in module or "privesc" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1548.003"), "name": "Abuse Elevation Control: Sudo"})
        report["risk_level"] = result_data.get("risk_level", "Low")
        report["summary"] = result_data.get("summary", "Privesc check completed.")
        details = result_data.get("details", [])
        for d in details: report["findings"].append(f"[{d.get('severity')}] {d.get('type')}: {d.get('detail')}")

    elif "defense_evasion" in module or "evasion" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1140"), "name": "Deobfuscate/Decode Files or Information"})
        report["risk_level"] = result_data.get("risk_level", "Medium")
        report["summary"] = result_data.get("summary", "Evasion test completed.")
        details = result_data.get("details", [])
        for d in details:
            status = "Succeeded" if d.get("success") else "Failed"
            report["findings"].append(f"Evasion Test '{d.get('technique')}': {status}")

    elif "credential" in module or "secret" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1552.001"), "name": "Unsecured Credentials: Credentials In Files"})
        report["risk_level"] = result_data.get("risk_level", "Low")
        report["summary"] = result_data.get("summary", "Secret scan completed.")
        details = result_data.get("details", [])
        for d in details: report["findings"].append(f"[{d.get('type')}] Found in {d.get('file')}:{d.get('line')}")

    elif "lateral_movement" in module:
        report["mitre_techniques"].append({"id": result_data.get("technique_id", "T1021"), "name": "Remote Services"})
        report["risk_level"] = result_data.get("risk_level", "Medium")
        report["summary"] = result_data.get("summary", "Lateral movement scan completed.")
        details = result_data.get("details", [])
        for d in details:
            report["findings"].append(f"Open Port {d.get('port')}/{d.get('service')} -> {d.get('state').upper()}")

    if not report.get("summary"): report["summary"] = f"Completed {module}."
    if not report["next_steps"]: report["next_steps"].append("No immediate automated next steps.")
    return report

@router.post("/lab/create")
def create_task(data: TaskCreate):
    global task_counter
    task_counter += 1
    task = {"id": task_counter, **data.model_dump(), "status": "pending", "result": None}
    task_db.append(task)
    return task

@router.get("/lab/next")
def get_next_task():
    for t in task_db:
        if t["status"] == "pending":
            t["status"] = "running"
            return t
    return {"message": "No tasks"}

@router.post("/lab/{task_id}/submit")
def submit(task_id: int, data: TaskResult):
    for t in task_db:
        if t["id"] == task_id:
            t["status"] = "completed"
            t["result"] = json.dumps(data.result)
            return {"status": "success"}
    return {"error": "not found"}

@router.get("/lab/analyze/{task_id}")
def analyze_task(task_id: int):
    for t in task_db:
        if t["id"] == task_id:
            result_data = {}
            if t["result"]:
                try: result_data = json.loads(t["result"])
                except: result_data = {"raw": t["result"]}
            
            ai_report = ask_llama({"module": t["module"], "target": t["target"], "result": result_data})
            if not ai_report:
                ai_report = analyze_results_fallback(t["module"], t["target"], result_data)
                ai_report["ai_engine"] = "Rule-based Fallback"
            else:
                ai_report["ai_engine"] = "NVIDIA NIM Llama"
            return ai_report
    return {"error": "Task not found"}

@router.get("/lab/tasks")
def list_tasks():
    return task_db
