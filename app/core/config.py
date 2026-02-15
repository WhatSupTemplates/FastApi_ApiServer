from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import computed_field, model_validator

class Settings(BaseSettings):
    
    APP_TITLE: str = "Backend Skeleton made by @WhatSupYap"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Clean FastAPI backend with authentication"

    # ============================================================
    # Database Configuration
    # ============================================================
    DB_TYPE: str = "sqlite"  # "sqlite" or "postgresql"
    
    # PostgreSQL fields (optional, required if DB_TYPE=postgresql)
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    
    # SQLite field (optional, required if DB_TYPE=sqlite)
    SQLITE_DB_PATH: str = "./data/app.db"

    # ============================================================
    # Redis Configuration (for caching, queues, etc.)
    # ============================================================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # ============================================================
    # API Server Configuration
    # ============================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ============================================================
    # Authentication Configuration
    # ============================================================
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    AES_SECRET_KEY: str = "your-aes-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============================================================
    # Computed Fields (Auto-generated URLs)
    # ============================================================
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """
        Generate database URL based on DB_TYPE.
        - SQLite: sqlite+aiosqlite:///path/to/db.db
        - PostgreSQL: postgresql+asyncpg://user:password@host:port/dbname
        """
        if self.DB_TYPE.lower() == "sqlite":
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"
        elif self.DB_TYPE.lower() == "postgresql":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            raise ValueError(f"Unsupported DB_TYPE: {self.DB_TYPE}")


settings = Settings()