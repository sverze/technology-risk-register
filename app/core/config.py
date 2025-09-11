import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Technology Risk Register"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).parent.parent.parent / 'risk_register.db'}",
    )

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8008",
        "http://127.0.0.1:8008",
        "http://frontend:3000",  # Docker network communication
        "*",  # Allow all origins for development (remove in production)
    ]

    # GCP
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_BUCKET_NAME: str = os.getenv("GCP_BUCKET_NAME", "")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
