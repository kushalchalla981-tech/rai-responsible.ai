from typing import Optional
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "RAI Audit Platform"
    debug: bool = False
    
    firebase_api_key: Optional[str] = None
    firebase_project_id: Optional[str] = None
    firebase_auth_domain: Optional[str] = None
    firebase_storage_bucket: Optional[str] = None
    
    gemini_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()