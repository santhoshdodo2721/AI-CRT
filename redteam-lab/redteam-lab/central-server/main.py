from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth.routes import router as auth_router
from api.agents.routes import router as agents_router
from api.campaigns.routes import router as campaigns_router
from api.tasks.routes import router as tasks_router
from api.ai.routes import router as ai_router
from api.ai.auto_attack import router as auto_attack_router
from api.reports.routes import router as reports_router
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

app.include_router(auth_router,      prefix="/api/auth",      tags=["auth"])
app.include_router(agents_router,    prefix="/api/agents",    tags=["agents"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(tasks_router,     prefix="/api/tasks",     tags=["tasks"])
app.include_router(ai_router,          prefix="/api/ai",        tags=["ai"])
app.include_router(auto_attack_router, prefix="/api/ai",        tags=["auto-attack"])
app.include_router(reports_router,     prefix="/api/reports",   tags=["reports"])

@app.get("/health")
def health():
    return {"status": "ok"}
