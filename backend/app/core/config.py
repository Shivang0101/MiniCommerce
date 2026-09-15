from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./minicommerce.db"
    READ_DATABASE_URL: str | None = None

    # Database Pool Settings
    DB_POOL_SIZE: int = 15
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800

    # Security & CORS Settings
    JWT_SECRET: str = "supersecretkey_minicommerce_v10_laboratory_key_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_COOKIE_NAME: str = "refresh_token"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300

    # ARQ Queue Settings
    ARQ_QUEUE_NAME: str = "arq:queue"
    TASK_MAX_RETRIES: int = 3
    TASK_TIMEOUT_SECONDS: int = 30

    # Rate Limit Settings (requests per minute)
    RATE_LIMIT_DEFAULT: int = 60
    RATE_LIMIT_AUTH: int = 10
    RATE_LIMIT_ADMIN: int = 120

    # Default Admin Credentials
    DEFAULT_ADMIN_EMAIL: str = "admin@minicommerce.com"
    DEFAULT_ADMIN_PASSWORD: str = "Admin@123456"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
