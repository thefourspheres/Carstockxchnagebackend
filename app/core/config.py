# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:Pass@localhost:5432/carstockxchange"

    # JWT
    JWT_SECRET: str = "SUPER_SECRET_KEY_123"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60



        # 🔔 ALERT EMAIL CONFIG (NEW)
    ALERT_EMAIL_FROM: str | None = None
    ALERT_EMAIL_PASSWORD: str | None = None
    ALERT_EMAIL_TO: str | None = None
    
    # Storage Configuration
    STORAGE_TYPE: str = "local"  # local, s3, cloudinary
    LOCAL_STORAGE_PATH: str = "uploads"
    
    # S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()