from typing import List, Optional, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import os
import json

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BACKEND_DIR, "spendsense.db").replace("\\", "/")

class Settings(BaseSettings):
    PROJECT_NAME: str = "SpendSense-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Server network binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Configuration
    # Defaults to backend/spendsense.db for immediate zero-config persistence, 
    # but seamlessly switches to PostgreSQL when DATABASE_URL is set in .env
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            # Render and some cloud providers provide postgres:// URIs
            # SQLAlchemy 1.4+ strictly requires postgresql://
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
        return v
    
    # Security & JWT Configuration
    SECRET_KEY: str = "spendsense-super-secret-dev-key-change-in-production-123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS Configuration: allow localhost & 127.0.0.1 on Vite ports, plus production domains
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]
    
    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_trimmed = v.strip()
            if v_trimmed.startswith("[") and v_trimmed.endswith("]"):
                try:
                    return json.loads(v_trimmed)
                except Exception:
                    pass
            # Comma-separated format support (e.g. "https://app.render.com,https://api.render.com" or "*")
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # AI Assistant Provider Configuration
    AI_PROVIDER: str = "mock"  # Options: 'mock', 'gemini', 'openai', 'groq'
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
