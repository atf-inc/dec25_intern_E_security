from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database - will be processed to remove unsupported parameters
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/dbname"

    # Auth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    SECRET_KEY: str = "your_secret_key_change_in_production"
    
    # Frontend URL for Redirects
    FRONTEND_URL: str = "http://localhost:3000"
    OAUTH_SUCCESS_REDIRECT_URL: str = "http://localhost:3000/dashboard"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    API_BASE_URL: str = "http://localhost:8001"


    
    # Environment
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file if it exists
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allow lowercase env vars to match uppercase field names
        extra="ignore"  # Ignore extra fields not defined in the model
    )

settings = Settings()