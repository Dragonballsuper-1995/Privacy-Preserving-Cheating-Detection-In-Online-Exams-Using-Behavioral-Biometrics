"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    environment: str = "development"
    debug: bool = True
    
    # Database - SQLite for dev, PostgreSQL for production
    database_url: str = "sqlite:///./data/cheating_detector.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # CORS
    cors_origins: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allowed_origins: str = "http://localhost:3000"  # For compatibility
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # ML Model Settings
    similarity_threshold: float = 0.85
    risk_threshold: float = 0.40  # Lowered further for better detection
    individual_score_threshold: float = 0.60  # Flag if ANY individual score exceeds this
    
    # Feature Extraction Settings
    min_pause_duration: int = 2000  # milliseconds
    max_typing_speed: int = 150  # WPM
    
    # Storage
    event_logs_dir: str = "data/event_logs"
    models_dir: str = "models"
    data_dir: str = "data"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

# Ensure directories exist
os.makedirs(settings.event_logs_dir, exist_ok=True)
os.makedirs(settings.models_dir, exist_ok=True)
os.makedirs(settings.data_dir, exist_ok=True)
