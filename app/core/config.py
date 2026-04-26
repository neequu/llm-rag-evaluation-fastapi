from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    REDIS_PORT: int = 6379

    APP_PORT: int = 8000
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str

    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def DATABASE_URL(self) -> str:
        """Build database URL from individual env vars"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def REDIS_URL(self) -> str:
        """Build Redis URL from port"""
        return f"redis://redis:{self.REDIS_PORT}/0"


settings = Settings()  # type: ignore
