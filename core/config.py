from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DEBUG: bool = False

    POSTGRES_USER: str = "hirebox"
    POSTGRES_PASSWORD: str = "hirebox"
    POSTGRES_DB: str = "hirebox"
    POSTGRES_HOST: str = "localhost"

    DATABASE_URL: str = ""

    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"

    # Mail
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    FRONTEND_URL: str = "http://localhost:8000"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "hirebox"
    MINIO_ROOT_PASSWORD: str = "hirebox123"
    MINIO_BUCKET: str = "hirebox-cvs"
    MINIO_SECURE: bool = False

    @model_validator(mode="after")
    def set_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}"
                f":{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()