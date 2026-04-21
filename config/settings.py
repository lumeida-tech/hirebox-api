from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_ENV: str = "development"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://hirebox:hirebox@localhost:5432/hirebox"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # MinIO (S3 compatible)
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ROOT_USER: str = "hirebox"
    MINIO_ROOT_PASSWORD: str = "hirebox123"
    MINIO_BUCKET: str = "hirebox-cvs"
    MINIO_SECURE: bool = False

    # NLP
    SPACY_MODEL: str = "xx_ent_wiki_sm"


settings = Settings()
