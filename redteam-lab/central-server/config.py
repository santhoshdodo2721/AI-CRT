import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://redteam:redteam@localhost:5432/redteamdb")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-a-long-random-string")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    
    AI_MAX_STEPS: int = int(os.getenv("AI_MAX_STEPS", "50"))
    AI_DECISION_TIMEOUT: int = int(os.getenv("AI_DECISION_TIMEOUT", "300"))
    TOOL_EXECUTION_TIMEOUT: int = int(os.getenv("TOOL_EXECUTION_TIMEOUT", "600"))

settings = Settings()
