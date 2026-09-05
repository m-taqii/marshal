from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # App
    app_env: str = "development"  # development | production
    log_level: str = "INFO"

    database_url: str = "sqlite:///./app.db"

    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model_id: Optional[str] = None

    # GitHub
    github_token: str
    github_webhook_secret: str  # verifies incoming webhook signatures (HMAC)

    # Discord
    discord_bot_token: str
    discord_notify_channel_id: int

@lru_cache
def get_settings() -> Settings:
    return Settings()