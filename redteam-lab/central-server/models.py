from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    status = Column(String, default="active")
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=True)
    module = Column(String)
    target = Column(String)
    status = Column(String, default="pending") # pending, running, completed
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=database.engine)