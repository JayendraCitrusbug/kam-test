from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Load from .env file at root


class Settings(BaseSettings):
    jwt_secret: str = "mocksecret"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
