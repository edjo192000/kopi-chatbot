# app/config.py
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_decode_responses: bool = True

    # Conversation Settings
    conversation_ttl_seconds: int = 3600  # 1 hour
    max_conversation_messages: int = 10  # 5 pairs of user/bot messages

    # API Settings
    api_timeout_seconds: int = 30
    log_level: str = "INFO"

    # Environment
    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()