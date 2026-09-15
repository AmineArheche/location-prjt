from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Scalable FastAPI REST API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_db"
    
    # Asynchronous DB URL (SQLite fallback for immediate out-of-the-box local testing, PostgreSQL supported)
    DATABASE_URL: str = "sqlite+aiosqlite:///./fastapi_demo.db"
    
    # Synchronous DB URL for Alembic migrations
    SYNC_DATABASE_URL: str = "sqlite:///./fastapi_demo.db"

    # JWT Security Settings
    SECRET_KEY: str = "super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours for easy testing

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
