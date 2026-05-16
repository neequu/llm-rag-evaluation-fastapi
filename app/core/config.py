from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Postgres ──────────────────────────────────────────────────────────────
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_PORT: int = 6379
    REDIS_HOST: str = "localhost"

    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"

    # ── MinIO / S3 ────────────────────────────────────────────────────────────
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "uploads"
    MINIO_USE_SSL: bool = False

    # ── App ───────────────────────────────────────────────────────────────────
    APP_PORT: int = 8000
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str

    CORS_ORIGINS: list[str]
    CORS_ALLOW_CREDENTIALS: bool

    # ── DB pool ───────────────────────────────────────────────────────────────
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Validators ────────────────────────────────────────────────────────────
    @field_validator("MINIO_ENDPOINT")
    @classmethod
    def endpoint_no_scheme(cls, v: str) -> str:
        """Guard against accidentally including http:// in the endpoint.
        The S3Client builds the URL itself; a double-scheme breaks boto3."""
        if v.startswith(("http://", "https://")):
            raise ValueError(
                f"MINIO_ENDPOINT must be host:port only, without a scheme. Got: {v!r}"
            )
        return v

    # ── Computed properties ───────────────────────────────────────────────────
    @property
    def DATABASE_URL(self) -> str:
        """Async-compatible SQLAlchemy URL."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def MINIO_URL(self) -> str:
        """Full URL used by the S3 client."""
        scheme = "https" if self.MINIO_USE_SSL else "http"
        return f"{scheme}://{self.MINIO_ENDPOINT}"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8002

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]
