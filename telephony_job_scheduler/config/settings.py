from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    APP_NAME: str = "Telephony Job Scheduler"
    API_VERSION: str = "v1"

    DATABASE_URL: str = "sqlite+aiosqlite:///./jobs.db"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


app_settings = AppSettings()
