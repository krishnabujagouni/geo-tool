"""
Configuration settings for GEO Tool
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    app_name: str = "GEO Tool"
    debug: bool = True
    
    # AI - Anthropic Claude
    anthropic_api_key: Optional[str] = None
    
    # Scraping
    user_agent: str = "GEOBot/1.0 (+https://geotool.dev)"
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
