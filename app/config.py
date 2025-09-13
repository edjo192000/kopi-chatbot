# app/config.py
import os
from typing import Optional
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application Configuration
    app_name: str = "Kopi Chatbot API"
    app_version: str = "2.0.0"
    environment: str = Field("development", alias="ENVIRONMENT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    api_timeout_seconds: int = 30

    # Redis Configuration
    redis_url: str = Field("redis://localhost:6379", alias="REDIS_URL")
    redis_db: int = 0
    redis_decode_responses: bool = True

    # Conversation Settings
    conversation_ttl_seconds: int = 3600  # 1 hour
    max_conversation_messages: int = 10

    # OpenAI API Configuration
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    openai_enabled: bool = True
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 150
    openai_temperature: float = 0.7
    openai_timeout: int = 30

    # Meta-Persuasion Configuration
    meta_persuasion_enabled: bool = Field(True, alias="META_PERSUASION_ENABLED")
    educational_mode_enabled: bool = Field(True, alias="EDUCATIONAL_MODE_ENABLED")
    educational_content_frequency: float = Field(0.3, alias="EDUCATIONAL_CONTENT_FREQUENCY")

    # Debate Service Configuration
    debate_educational_mode: bool = True
    debate_analysis_enabled: bool = True

    # CORS Configuration
    cors_origins: list = ["*"]  # Configure appropriately for production
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Security Configuration
    max_message_length: int = 2000
    rate_limit_enabled: bool = False  # To be implemented
    rate_limit_requests_per_minute: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_settings()

    def _validate_settings(self):
        """Validate configuration settings"""

        # Validate educational content frequency
        if not 0.0 <= self.educational_content_frequency <= 1.0:
            raise ValueError("educational_content_frequency must be between 0.0 and 1.0")

        # Validate conversation TTL
        if self.conversation_ttl_seconds < 60:
            raise ValueError("conversation_ttl_seconds must be at least 60 seconds")

        # Validate max conversation messages
        if self.max_conversation_messages < 2:
            raise ValueError("max_conversation_messages must be at least 2")

        # Validate OpenAI settings
        if self.openai_enabled and not self.openai_api_key:
            import logging
            logging.getLogger(__name__).warning(
                "OpenAI is enabled but no API key provided. Will use fallback responses."
            )

        # Validate message length
        if self.max_message_length < 10:
            raise ValueError("max_message_length must be at least 10 characters")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"

    @property
    def redis_config(self) -> dict:
        """Get Redis connection configuration"""
        return {
            "url": self.redis_url,
            "db": self.redis_db,
            "decode_responses": self.redis_decode_responses
        }

    @property
    def openai_config(self) -> dict:
        """Get OpenAI configuration"""
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature,
            "timeout": self.openai_timeout,
            "enabled": self.openai_enabled and bool(self.openai_api_key)
        }

    @property
    def meta_persuasion_config(self) -> dict:
        """Get meta-persuasion configuration"""
        return {
            "enabled": self.meta_persuasion_enabled,
            "educational_mode": self.educational_mode_enabled,
            "educational_frequency": self.educational_content_frequency
        }

    @property
    def cors_config(self) -> dict:
        """Get CORS configuration"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers
        }

    def get_summary(self) -> dict:
        """Get configuration summary for logging/debugging"""
        return {
            "app_name": self.app_name,
            "version": self.app_version,
            "environment": self.environment,
            "redis_configured": bool(self.redis_url),
            "openai_configured": bool(self.openai_api_key),
            "meta_persuasion_enabled": self.meta_persuasion_enabled,
            "educational_mode": self.educational_mode_enabled,
            "max_conversation_messages": self.max_conversation_messages,
            "conversation_ttl_hours": self.conversation_ttl_seconds / 3600
        }


# Global settings instance
settings = Settings()


# Validation functions for specific components
def validate_openai_settings() -> bool:
    """Validate OpenAI configuration"""
    if not settings.openai_enabled:
        return True

    if not settings.openai_api_key:
        return False

    if settings.openai_max_tokens < 10 or settings.openai_max_tokens > 4000:
        return False

    if not 0.0 <= settings.openai_temperature <= 2.0:
        return False

    return True


def validate_redis_settings() -> bool:
    """Validate Redis configuration"""
    if not settings.redis_url:
        return False

    if not settings.redis_url.startswith(('redis://', 'rediss://')):
        return False

    return True


def validate_meta_persuasion_settings() -> bool:
    """Validate meta-persuasion configuration"""
    if not isinstance(settings.meta_persuasion_enabled, bool):
        return False

    if not isinstance(settings.educational_mode_enabled, bool):
        return False

    if not 0.0 <= settings.educational_content_frequency <= 1.0:
        return False

    return True


# Configuration validation on import
def validate_all_settings() -> dict:
    """Validate all configuration settings"""
    validation_results = {
        "openai": validate_openai_settings(),
        "redis": validate_redis_settings(),
        "meta_persuasion": validate_meta_persuasion_settings()
    }

    return validation_results


# Export commonly used settings
__all__ = [
    "settings",
    "validate_openai_settings",
    "validate_redis_settings",
    "validate_meta_persuasion_settings",
    "validate_all_settings"
]