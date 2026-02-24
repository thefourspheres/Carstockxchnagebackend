from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database (NO DEFAULT)
    DATABASE_URL: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Alert Email
    ALERT_EMAIL_FROM: Optional[str] = None
    ALERT_EMAIL_PASSWORD: Optional[str] = None
    ALERT_EMAIL_TO: Optional[str] = None

    # Storage
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_PATH: str = "uploads"

    # S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()