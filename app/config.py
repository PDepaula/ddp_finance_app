from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Financial Tracker"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./financial_tracker.db"
    ASYNC_DATABASE_URL: str = "sqlite+aiosqlite:///./financial_tracker.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key"  # Change this in production!
    
    # In Pydantic v2, the Config class is replaced with model_config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

@lru_cache()
def get_settings() -> Settings:
    """Return cached settings"""
    return Settings()

settings = get_settings()