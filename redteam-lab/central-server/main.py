from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.mitre_routes import router as mitre_router
from api.lab_routes import router as lab_router
from api.auth.routes import router as auth_router
from api.agents.routes import router as agents_router
from api.campaigns.routes import router as campaigns_router
from api.tasks.routes import router as tasks_router
from api.ai.routes import router as ai_router
from api.reports.routes import router as reports_router
from api.dashboard.routes import router as dashboard_router
from database.db import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RedTeam Lab Central Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mitre_router,   prefix="/api/mitre",    tags=["MITRE"])
app.include_router(lab_router,     prefix="/api",          tags=["Lab"])

app.include_router(auth_router,      prefix="/api/auth",      tags=["auth"])
app.include_router(agents_router,    prefix="/api/agents",    tags=["agents"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(tasks_router,     prefix="/api/tasks",     tags=["tasks"])
app.include_router(ai_router,        prefix="/api/ai",        tags=["ai"])
app.include_router(reports_router,   prefix="/api/reports",   tags=["reports"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/health")
def health():
    return {"status": "ok"}
