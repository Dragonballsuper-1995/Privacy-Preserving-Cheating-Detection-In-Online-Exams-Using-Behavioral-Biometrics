"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database - SQLite for dev, PostgreSQL for production
    database_url: str = "sqlite:///./data/cheating_detector.db"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # ML Model Settings
    similarity_threshold: float = 0.85
    risk_threshold: float = 0.75
    
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
