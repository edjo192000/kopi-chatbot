# app/config.py
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application Configuration
    app_name: str = "Kopi Chatbot API"
    app_version: str = "2.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    api_timeout_seconds: int = 30

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_db: int = 0
    redis_decode_responses: bool = True

    # Conversation Settings
    conversation_ttl_seconds: int = 3600  # 1 hour
    max_conversation_messages: int = 10

    # OpenAI API Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_enabled: bool = True
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 150
    openai_temperature: float = 0.7
    openai_timeout: int = 30

    # Meta-Persuasion Configuration
    meta_persuasion_enabled: bool = Field(default=True, env="META_PERSUASION_ENABLED")
    educational_mode_enabled: bool = Field(default=True, env="EDUCATIONAL_MODE_ENABLED")
    educational_content_frequency: float = Field(default=0.3, env="EDUCATIONAL_CONTENT_FREQUENCY")

    # Debate Service Configuration
    debate_educational_mode: bool = True
    debate_analysis_enabled: bool = True

    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]

    # Security Configuration
    max_message_length: int = 2000
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # DEBUGGING MAS AGRESIVO
        print("🔥 DEBUGGING RAILWAY VARIABLES:")
        print("=" * 50)

        # Debug direct OS environment
        print(f"Direct os.getenv('OPENAI_API_KEY'): {bool(os.getenv('OPENAI_API_KEY'))}")
        print(f"Direct os.getenv('REDIS_URL'): {os.getenv('REDIS_URL', 'NOT_SET')}")

        # Debug all Railway vars
        railway_vars = {k: v for k, v in os.environ.items() if 'RAILWAY' in k or 'REDIS' in k or 'OPENAI' in k}
        print(f"Railway-related env vars: {list(railway_vars.keys())}")

        # Debug loaded values
        print(f"🔍 OPENAI_API_KEY loaded: {'✅ Yes' if self.openai_api_key else '❌ No'}")
        print(f"🔍 REDIS_URL: {self.redis_url}")
        print("=" * 50)

        self._validate_settings()

    def _validate_settings(self):
        """Validate configuration settings"""
        if not 0.0 <= self.educational_content_frequency <= 1.0:
            raise ValueError("educational_content_frequency must be between 0.0 and 1.0")

        if self.conversation_ttl_seconds < 60:
            raise ValueError("conversation_ttl_seconds must be at least 60 seconds")

        if self.max_conversation_messages < 2:
            raise ValueError("max_conversation_messages must be at least 2")

        if self.openai_enabled and not self.openai_api_key:
            import logging
            logging.getLogger(__name__).warning(
                "OpenAI is enabled but no API key provided. Will use fallback responses."
            )

        if self.max_message_length < 10:
            raise ValueError("max_message_length must be at least 10 characters")

    @property
    def redis_config(self) -> dict:
        return {
            "url": self.redis_url,
            "db": self.redis_db,
            "decode_responses": self.redis_decode_responses
        }

    @property
    def openai_config(self) -> dict:
        return {
            "api_key": self.openai_api_key,
            "model": self.openai_model,
            "max_tokens": self.openai_max_tokens,
            "temperature": self.openai_temperature,
            "timeout": self.openai_timeout,
            "enabled": self.openai_enabled and bool(self.openai_api_key)
        }


# Global settings instance
settings = Settings()