"""Application configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    model_config = {"env_file": ".env"}

    api_key: str = ""
    rapidapi_proxy_secret: str = ""
    port: int = 8000
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
