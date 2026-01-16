"""
Shrestha Capital - Configuration Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    google_api_key: str

    # Database
    database_url: str = "sqlite+aiosqlite:///./shrestha_capital.db"

    # Environment
    environment: str = "development"
    debug: bool = True

    # Gemini Model Settings
    gemini_pro_model: str = "gemini-2.5-pro-preview-06-05"
    gemini_flash_model: str = "gemini-2.0-flash"

    # Agent Settings
    default_temperature: float = 0.7
    max_output_tokens: int = 8192

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
