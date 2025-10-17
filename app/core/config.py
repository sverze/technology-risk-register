import os
import json
from pathlib import Path
from typing import List, Union

from pydantic import field_validator
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

    # CORS - can be JSON string, list, or "*" for all origins
    ALLOWED_ORIGINS: Union[str, List[str]] = os.getenv(
        "ALLOWED_ORIGINS",
        '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080", "http://frontend:3000"]'
    )

    @field_validator('ALLOWED_ORIGINS')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle wildcard for all origins
            if v == "*":
                return ["*"]
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle gcloud alternate delimiter format (^;^value1;value2)
                if v.startswith("^;^"):
                    return [origin.strip() for origin in v[3:].split(";")]
                # Fallback to split by comma
                return [origin.strip() for origin in v.split(",")]
        return v

    # GCP
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")
    GCP_BUCKET_NAME: str = os.getenv("GCP_BUCKET_NAME", "")

    # Authentication
    AUTH_USERNAME: str = os.getenv("AUTH_USERNAME", "admin")
    AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "changeme")
    AUTH_SECRET_KEY: str = os.getenv(
        "AUTH_SECRET_KEY",
        "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # Default for local dev only
    )
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Short-lived access tokens
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Long-lived refresh tokens

    # Anthropic API (for Risk SME Chat feature)
    ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY", None)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
