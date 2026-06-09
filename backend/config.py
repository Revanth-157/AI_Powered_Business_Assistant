"""
Configuration management for FastAPI backend.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # App Settings
    APP_NAME: str = "FMCG BI Assistant"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    WORKERS: int = int(os.getenv("WORKERS", "4"))
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/fmcg_ai"
    )
    DATABASE_ECHO: bool = DEBUG
    
    # SQLite Fallback (for development)
    SQLITE_DB_PATH: str = os.getenv(
        "SQLITE_DB_PATH",
        "../architecture/fmcg_analytics.db"
    )
    USE_SQLITE: bool = os.getenv("USE_SQLITE", "False").lower() == "true"
    
    # JWT/Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",  # Streamlit
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8501",
    ]
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    ENABLE_LLM: bool = OPENAI_API_KEY is not None
    
    # AI Agents
    AI_DATABASE_PATH: str = os.getenv(
        "AI_DATABASE_PATH",
        "../architecture/fmcg_analytics.db"
    )
    AGENT_TIMEOUT: int = int(os.getenv("AGENT_TIMEOUT", "60"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    # Session/Cache
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()
