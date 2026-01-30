from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type safety.
    """
    
    # Database Configuration
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = ""  # Empty string allows app to start without key
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 1000
    
    # Application Settings
    APP_NAME: str = "Personal Knowledge Vault"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Vector Search Settings
    VECTOR_DIMENSIONS: int = 1536
    TOP_K_RESULTS: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars not defined here
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.startswith("sk-"))
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_required_for_ai(self) -> None:
        """
        Validate that AI-related config is present.
        Call this before making OpenAI API calls.
        """
        if not self.is_openai_configured:
            raise ValueError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY in your .env file."
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Create and cache settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()


# Convenience instance for direct imports
settings = get_settings()