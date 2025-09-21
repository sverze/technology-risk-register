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
        '["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8008", "http://127.0.0.1:8008", "http://frontend:3000"]'
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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
