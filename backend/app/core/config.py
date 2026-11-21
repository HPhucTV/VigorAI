# [OWNER: M3] Cau hinh ung dung FastAPI
import json
import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "VigorAI API"
    DATABASE_URL: str = (
        "postgresql+asyncpg://gym3d_user:gym3d_dev_password@localhost:5432/gym3d_db"
    )
    JWT_SECRET_KEY: str = "change-me-in-production-via-env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin_password"
    S3_BUCKET_NAME: str = "gym3d-assets"
    S3_REGION: str = "us-east-1"
    S3_PUBLIC_BASE_URL: str = "http://localhost:9000/gym3d-assets"
    S3_ADDRESSING_STYLE: str = ""
    API_PUBLIC_BASE_URL: str = ""
    LOCAL_GLB_ASSETS_DIR: str = ""
    CORS_ORIGINS: Any = ["*"]
    RUN_MIGRATIONS_ON_STARTUP: bool = True
    RUN_SEED_ON_STARTUP: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def resolved_api_public_base_url(self) -> str:
        """Tra ve HTTPS base URL cong khai cua API neu da cau hinh hoac dang chay tren Railway."""
        explicit = (self.API_PUBLIC_BASE_URL or "").strip().rstrip("/")
        if explicit:
            return explicit
        railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "").strip()
        if railway_domain:
            if railway_domain.startswith(("http://", "https://")):
                return railway_domain.rstrip("/")
            return f"https://{railway_domain}"
        return ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        raw = value.strip()
        if not raw:
            return raw

        parts = urlsplit(raw)
        scheme = parts.scheme.lower()
        if scheme in {"postgres", "postgresql", "postgresql+psycopg2"}:
            scheme = "postgresql+asyncpg"

        query_items = parse_qsl(parts.query, keep_blank_values=True)
        has_ssl = any(k.lower() == "ssl" for k, _ in query_items)
        normalized_query: list[tuple[str, str]] = []
        for key, val in query_items:
            if key.lower() == "sslmode":
                if val.strip().lower() == "disable" or has_ssl:
                    continue
                normalized_query.append(("ssl", val))
                has_ssl = True
            else:
                normalized_query.append((key, val))

        return urlunsplit(
            (
                scheme,
                parts.netloc,
                parts.path,
                urlencode(normalized_query),
                parts.fragment,
            )
        )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if not isinstance(value, str):
            return value

        raw = value.strip()
        if not raw:
            return ["*"]

        if raw.startswith("["):
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]

        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings()
