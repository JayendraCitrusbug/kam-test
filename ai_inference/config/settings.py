from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    JWT_SECRET: str = "mocksecret"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
