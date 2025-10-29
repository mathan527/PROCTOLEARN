import os
from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "ProctoLearn"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: str
    REDIS_URL: str
    
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173"
    
    GROQ_API_KEY: str
    
    UPLOAD_DIR: Path = Path("uploads")
    PROCTORING_LOGS_DIR: Path = Path("proctoring_logs")
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = os.path.join(Path(__file__).parent.parent.parent, ".env")
        case_sensitive = True
        extra = "ignore"

settings = Settings()
