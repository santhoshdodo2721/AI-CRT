from sqlalchemy import create_engine, Column, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://redteam:redteam@localhost:5432/redteamdb")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def new_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id       = Column(String, primary_key=True, default=new_uuid)
    username = Column(String, unique=True, nullable=False)
    email    = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)          # bcrypt hash
    role     = Column(Enum("admin", "operator", "viewer", name="user_role"), default="operator")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"
    id           = Column(String, primary_key=True, default=new_uuid)
    name         = Column(String, nullable=False)
    hostname     = Column(String)
    ip_address   = Column(String)
    os_info      = Column(String)
    status       = Column(Enum("online", "offline", "idle", name="agent_status"), default="offline")
    last_seen    = Column(DateTime)
    registered_at = Column(DateTime, default=datetime.datetime.utcnow)
    tasks        = relationship("Task", back_populates="agent")


class Campaign(Base):
    __tablename__ = "campaigns"
    id          = Column(String, primary_key=True, default=new_uuid)
    name        = Column(String, nullable=False)
    description = Column(Text)
    target      = Column(String, nullable=False)   # IP / domain / CIDR
    status      = Column(Enum("created", "running", "paused", "completed", name="campaign_status"), default="created")
    created_by  = Column(String, ForeignKey("users.id"))
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    tasks       = relationship("Task", back_populates="campaign")


class Task(Base):
    __tablename__ = "tasks"
    id           = Column(String, primary_key=True, default=new_uuid)
    campaign_id  = Column(String, ForeignKey("campaigns.id"))
    agent_id     = Column(String, ForeignKey("agents.id"), nullable=True)
    module       = Column(String, nullable=False)   # e.g. recon.nmap_scan
    params       = Column(JSON, default={})
    status       = Column(Enum("pending", "assigned", "running", "completed", "failed", name="task_status"), default="pending")
    result       = Column(JSON, nullable=True)
    mitre_id     = Column(String, nullable=True)    # e.g. T1046
    severity     = Column(String, nullable=True)
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    campaign     = relationship("Campaign", back_populates="tasks")
    agent        = relationship("Agent", back_populates="tasks")


class Finding(Base):
    __tablename__ = "findings"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    task_id     = Column(String, ForeignKey("tasks.id"))
    title       = Column(String)
    description = Column(Text)
    severity    = Column(Enum("critical", "high", "medium", "low", "info", name="severity"), default="info")
    mitre_id    = Column(String, nullable=True)
    remediation = Column(Text, nullable=True)
    raw_output  = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)


class Report(Base):
    __tablename__ = "reports"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    content     = Column(Text)
    format      = Column(Enum("json", "markdown", "pdf", name="report_format"), default="markdown")
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
