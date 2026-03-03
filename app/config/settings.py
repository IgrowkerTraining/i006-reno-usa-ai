"""Application settings and configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    app_name: str = "FastAPI AI Template"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # OpenRouter Configuration
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # --- Database Configuration ---
    # DATABASE_URL es la que usará SQLAlchemy para la conexión
    database_url: str
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # CORS Configuration
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Logging Configuration
    log_level: str = "INFO"
    
    # Usamos model_config para leer el .env
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore" 
    )


# Global settings instance
settings = Settings()
