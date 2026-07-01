from sqlalchemy import create_engine, Column, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
import os

from config import settings

DATABASE_URL = settings.DATABASE_URL

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
    status       = Column(Enum("online", "offline", "idle", "running", name="agent_status"), default="offline")
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
    
    # New AI-driven fields
    credentials  = Column(JSON, default=[])       # List of provided credentials
    scope_config = Column(JSON, default={})       # Scope rules (what to test/skip)
    ai_enabled   = Column(Boolean, default=True)  # Run via AI orchestrator or manually
    
    tasks       = relationship("Task", back_populates="campaign")
    host_memories = relationship("HostMemory", back_populates="campaign")
    credential_stores = relationship("CredentialStore", back_populates="campaign")
    ai_decisions = relationship("AIDecisionLog", back_populates="campaign")
    tool_executions = relationship("ToolExecution", back_populates="campaign")
    campaign_memory = relationship("CampaignMemory", back_populates="campaign", uselist=False)


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


# ── AI Memory Models ──────────────────────────────────────────────────────────

class HostMemory(Base):
    __tablename__ = "host_memory"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    ip_address  = Column(String, nullable=False)
    hostname    = Column(String, nullable=True)
    os_info     = Column(String, nullable=True)
    open_ports  = Column(JSON, default=[])         # List of int
    services    = Column(JSON, default={})         # Port to service mapping
    vulns       = Column(JSON, default=[])
    state       = Column(JSON, default={})         # Generic key-value state for this host
    updated_at  = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    campaign    = relationship("Campaign", back_populates="host_memories")


class CredentialStore(Base):
    __tablename__ = "credential_store"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    username    = Column(String, nullable=False)
    password    = Column(String, nullable=True)    # Or hash/key
    cred_type   = Column(String, default="password") # password, hash, key, token
    source      = Column(String, default="provided") # provided, discovered
    valid_on    = Column(JSON, default=[])         # List of target IPs/services where this worked
    tested_on   = Column(JSON, default=[])         # Where it was already tried
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    campaign    = relationship("Campaign", back_populates="credential_stores")


class AIDecisionLog(Base):
    __tablename__ = "ai_decision_log"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    step        = Column(Integer, nullable=False)
    state_summary = Column(Text)                   # What AI saw
    reasoning   = Column(Text)                     # Why AI chose action
    action      = Column(String)                   # What AI decided to do (e.g. "run_tool")
    tool_name   = Column(String, nullable=True)
    tool_params = Column(JSON, nullable=True)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    campaign    = relationship("Campaign", back_populates="ai_decisions")


class CampaignMemory(Base):
    __tablename__ = "campaign_memory"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"), unique=True)
    phase       = Column(String, default="recon")  # recon, vuln, exploit, post_exploit, report
    completion_pct = Column(Integer, default=0)
    risk_score  = Column(Integer, default=0)
    global_state = Column(JSON, default={})        # Any campaign-wide facts
    updated_at  = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    campaign    = relationship("Campaign", back_populates="campaign_memory")


class ToolExecution(Base):
    __tablename__ = "tool_execution"
    id          = Column(String, primary_key=True, default=new_uuid)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    task_id     = Column(String, ForeignKey("tasks.id"), nullable=True)
    tool_name   = Column(String, nullable=False)
    params      = Column(JSON, default={})
    status      = Column(String, default="running") # running, completed, failed
    start_time  = Column(DateTime, default=datetime.datetime.utcnow)
    end_time    = Column(DateTime, nullable=True)
    raw_output  = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    error       = Column(Text, nullable=True)
    campaign    = relationship("Campaign", back_populates="tool_executions")

