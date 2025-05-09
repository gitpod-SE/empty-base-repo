import os
from typing import List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API
    API_PREFIX: str = "/api"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = ENV == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
