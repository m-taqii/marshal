from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_env: str = "development"  # development | production
    log_level: str = "INFO"

    database_url: str

    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    llm_api_key: Optional[str] = None

    # GitHub
    github_token: str
    github_webhook_secret: str  # verifies incoming webhook signatures (HMAC)

    # Discord
    discord_bot_token: str
    discord_notify_channel_id: int

@lru_cache
def get_settings() -> Settings:
    return Settings()