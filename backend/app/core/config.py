from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be overridden via environment variables.
    """

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Transl8"
    API_VERSION: str = "v1"
    SECRET_KEY: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 0

    # Redis
    REDIS_URL: str

    # Clerk Authentication
    CLERK_JWT_PUBLIC_KEY: str
    CLERK_API_KEY: Optional[str] = None

    # Translation APIs
    DEEPL_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # File Storage
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "transl8-documents"
    S3_REGION: str = "auto"

    # File Upload Limits
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def api_prefix(self) -> str:
        """Get API prefix path."""
        return f"/api/{self.API_VERSION}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()
