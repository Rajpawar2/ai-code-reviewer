from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "AI Code Review & Debugging Assistant"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/code_reviewer",
        description="Database connection URL",
    )

    @property
    def normalized_database_url(self) -> str:
        """Normalizes standard postgres:// or postgresql:// URLs (e.g. from Render) to postgresql+psycopg://."""
        url = self.DATABASE_URL.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            return "postgresql+psycopg://" + url[len("postgresql://"):]
        return url

    # Security & Auth
    SECRET_KEY: str = "super_secret_jwt_key_change_in_production_development_key_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # AI Configuration
    AI_PROVIDER: str = "ollama"  # "ollama" or "mock"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    OLLAMA_TIMEOUT_SECONDS: float = 90.0

    # GitHub Service Limits
    GITHUB_TOKEN: str = ""
    MAX_REPO_FILES: int = 40
    MAX_REPO_TOTAL_SIZE_KB: int = 10000  # 10MB
    MAX_SINGLE_FILE_SIZE_KB: int = 500  # 500KB

    # Frontend URL & CORS
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    def get_cors_origins(self) -> List[str]:
        origins = list(self.CORS_ORIGINS)
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL.rstrip("/"))
        return origins


settings = Settings()
