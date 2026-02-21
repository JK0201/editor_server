from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    app: str = Field("app.main:app")
    host: str = Field("0.0.0.0")
    port: int = Field(8000)
    reload: bool = Field(False)

    class Config:
        env_file = BASE_DIR / ".env"  # fallback to .env file
        env_file_encoding = "utf-8"


# cache settings
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
