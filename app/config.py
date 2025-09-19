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

    # OpenAI API Configuration (Legacy - kept for backwards compatibility)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_enabled: bool = True
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 150
    openai_temperature: float = 0.7
    openai_timeout: int = 30

    # Anthropic Claude API Configuration (New Primary AI Provider)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_enabled: bool = True
    anthropic_model: str = Field(default="claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=200, env="ANTHROPIC_MAX_TOKENS")
    anthropic_timeout: int = Field(default=30, env="ANTHROPIC_TIMEOUT")

    # AI Provider Selection (prioritize Anthropic over OpenAI)
    preferred_ai_provider: str = Field(default="anthropic", env="AI_PROVIDER")  # "anthropic" or "openai"

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
        self._validate_settings()

    def _validate_settings(self):
        """Validate configuration settings"""
        import logging
        logging.getLogger(__name__).info(f"🔍 DEBUG: ANTHROPIC_API_KEY in env = {'ANTHROPIC_API_KEY' in os.environ}")
        logging.getLogger(__name__).info(f"🔍 DEBUG: ANTHROPIC_API_KEY value = {os.environ.get('ANTHROPIC_API_KEY', 'NOT_FOUND')[:20]}...")
        logging.getLogger(__name__).info(
            f"🔍 DEBUG: self.anthropic_api_key = {self.anthropic_api_key[:20] if self.anthropic_api_key else 'None'}...")

        if not 0.0 <= self.educational_content_frequency <= 1.0:
            raise ValueError("educational_content_frequency must be between 0.0 and 1.0")

        if self.conversation_ttl_seconds < 60:
            raise ValueError("conversation_ttl_seconds must be at least 60 seconds")

        if self.max_conversation_messages < 2:
            raise ValueError("max_conversation_messages must be at least 2")

        # Validate AI provider configuration
        if self.preferred_ai_provider not in ["anthropic", "openai"]:
            raise ValueError("preferred_ai_provider must be either 'anthropic' or 'openai'")

        # Check if preferred AI provider is properly configured
        if self.preferred_ai_provider == "anthropic":
            if self.anthropic_enabled and not self.anthropic_api_key:
                import logging
                logging.getLogger(__name__).warning(
                    "Anthropic is enabled and preferred but no API key provided. Will try OpenAI fallback or use fallback responses."
                )

        if self.preferred_ai_provider == "openai":
            if self.openai_enabled and not self.openai_api_key:
                import logging
                logging.getLogger(__name__).warning(
                    "OpenAI is enabled and preferred but no API key provided. Will try Anthropic fallback or use fallback responses."
                )

        # Warn if no AI providers are configured
        if not (self.anthropic_api_key or self.openai_api_key):
            import logging
            logging.getLogger(__name__).warning(
                "No AI provider API keys configured. Will use fallback responses only."
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

    @property
    def anthropic_config(self) -> dict:
        """Get Anthropic configuration"""
        return {
            "api_key": self.anthropic_api_key,
            "model": self.anthropic_model,
            "max_tokens": self.anthropic_max_tokens,
            "timeout": self.anthropic_timeout,
            "enabled": self.anthropic_enabled and bool(self.anthropic_api_key)
        }

    @property
    def active_ai_config(self) -> dict:
        """Get configuration for the currently active AI provider"""
        if self.preferred_ai_provider == "anthropic" and self.anthropic_config["enabled"]:
            return {**self.anthropic_config, "provider": "anthropic"}
        elif self.preferred_ai_provider == "openai" and self.openai_config["enabled"]:
            return {**self.openai_config, "provider": "openai"}
        elif self.anthropic_config["enabled"]:  # Fallback to Anthropic if available
            return {**self.anthropic_config, "provider": "anthropic"}
        elif self.openai_config["enabled"]:  # Fallback to OpenAI if available
            return {**self.openai_config, "provider": "openai"}
        else:
            return {"provider": "fallback", "enabled": False}

    def is_ai_available(self) -> bool:
        """Check if any AI provider is available"""
        return self.anthropic_config["enabled"] or self.openai_config["enabled"]

    def get_ai_status(self) -> dict:
        """Get status of all AI providers"""
        return {
            "preferred_provider": self.preferred_ai_provider,
            "anthropic": {
                "available": self.anthropic_config["enabled"],
                "model": self.anthropic_model
            },
            "openai": {
                "available": self.openai_config["enabled"],
                "model": self.openai_model
            },
            "active_provider": self.active_ai_config["provider"],
            "fallback_enabled": True
        }


# Global settings instance
settings = Settings()