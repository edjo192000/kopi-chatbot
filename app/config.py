# app/config.py
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # OpenAI Configuration (optional for now)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"  # Cost-effective model
    openai_max_tokens: int = 500
    openai_temperature: float = 0.8  # Creative but controlled
    openai_timeout: int = 30
    openai_enabled: bool = True  # Can disable OpenAI fallback to hardcoded responses

    # Environment
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()