from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    S3_ACCESS_KEY: str
    S3_ACCESS_SECRET: str
    S3_BUCKET_NAME: str
    S3_BRONZE_FOLDER_NAME: Optional[str] = None
    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DB: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
