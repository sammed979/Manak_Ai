from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationError
from typing import Optional
import warnings
import sys


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Application
    APP_NAME: str = "MANAK AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DEMO_MODE: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    USE_DOCKER_DB: bool = False
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/manak_ai"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_REFRESH_SECRET: str = "your-refresh-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Providers
    LLM_PROVIDER: str = "mock"  # "openai" | "mock"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"

    EMBEDDING_PROVIDER: str = "mock"  # "openai" | "mock"
    EMBEDDING_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Storage
    STORAGE_BUCKET: Optional[str] = None
    STORAGE_ACCESS_KEY: Optional[str] = None
    STORAGE_SECRET_KEY: Optional[str] = None

    # OCR
    OCR_PROVIDER: str = "none"  # "tesseract" | "none"

    # Translation
    TRANSLATION_PROVIDER: str = "mock"  # "mock" | "google"

    # Speech
    SPEECH_PROVIDER: str = "mock"

    # CORS
    # Supports wildcards (e.g. "https://*.vercel.app") and comma-separated strings.
    # Always includes localhost dev URLs plus *.vercel.app preview wildcard so
    # every new Vercel preview build works without re-configuring this list.
    CORS_ORIGINS: object = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, v):
        base = {
            "http://localhost:5173",
            "http://localhost:3000",
            "https://*.vercel.app",
        }
        if isinstance(v, str):
            for part in v.split(","):
                p = part.strip()
                if p:
                    base.add(p)
        elif isinstance(v, (list, tuple, set)):
            for p in v:
                if isinstance(p, str) and p.strip():
                    base.add(p.strip())
        ordered = []
        for pattern in (
            "http://localhost:5173",
            "http://localhost:3000",
            "https://*.vercel.app",
        ):
            if pattern in base:
                ordered.append(pattern)
                base.discard(pattern)
        ordered.extend(sorted(base))
        return ordered

    @field_validator("DEBUG", mode="after")
    @classmethod
    def validate_production_secrets(cls, v: bool) -> bool:
        # This runs *after* parsing both DEBUG and the secrets.
        # We can't access sibling values directly in a per-field validator;
        # we perform the check in a model_validator below. Keep validator to
        # preserve type coercion.
        return v


try:
    settings = Settings()
except ValidationError as e:
    print(f"Failed to load settings: {e}", file=sys.stderr)
    sys.exit(1)


# Production sanity checks
if not settings.DEBUG:
    defaults = [
        ("JWT_SECRET", "your-secret-key-change-in-production"),
        ("JWT_REFRESH_SECRET", "your-refresh-secret-key-change-in-production"),
    ]
    for name, default in defaults:
        if getattr(settings, name, None) == default:
            warnings.warn(
                f"Production mode detected but {name} still uses the default value. "
                f"Please set a secure secret via environment variables.",
                RuntimeWarning,
            )
