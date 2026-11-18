# [OWNER: M3] Cau hinh ung dung FastAPI
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
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
