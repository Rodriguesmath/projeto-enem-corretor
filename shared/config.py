from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "API de Correção de Redação ENEM"
    VERSION: str = "1.0.0"
    
    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "supersecret"
    POSTGRES_DB: str = "enem_correcoes_db"

    # Worker / Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # LLM Keys
    GOOGLE_API_KEY: Optional[str] = None
    PPLX_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "models/gemini-1.5-flash"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
