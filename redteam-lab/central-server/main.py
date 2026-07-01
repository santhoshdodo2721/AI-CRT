from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth.routes import router as auth_router
from api.agents.routes import router as agents_router
from api.campaigns.routes import router as campaigns_router
from api.tasks.routes import router as tasks_router
from api.ai.routes import router as ai_router
from api.reports.routes import router as reports_router
from api.dashboard.routes import router as dashboard_router
from api.websocket.routes import router as websocket_router
from database.db import engine, Base, SessionLocal, User
from api.auth.utils import hash_password

Base.metadata.create_all(bind=engine)

def seed_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@redteam.local",
                password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin_user)
        else:
            admin.password = hash_password("admin123")
        db.commit()
    finally:
        db.close()

seed_admin()

app = FastAPI(title="RedTeam Lab Central Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.lab.routes import router as lab_router

app.include_router(auth_router,      prefix="/api/auth",      tags=["auth"])
app.include_router(agents_router,    prefix="/api/agents",    tags=["agents"])
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(tasks_router,     prefix="/api/tasks",     tags=["tasks"])
app.include_router(ai_router,        prefix="/api/ai",        tags=["ai"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(lab_router,       prefix="/api/lab",       tags=["Lab"])
app.include_router(websocket_router, tags=["Websocket"])

@app.get("/health")
def health():
    return {"status": "ok"}
