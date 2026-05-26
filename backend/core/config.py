"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Platform-side backend settings.

    V1 demo does not expose model endpoint, API key, or provider selection to users.
    Those settings should remain platform runtime configuration.
    """

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HACKSON_", extra="ignore")

    app_env: str = Field(default="development")
    mongo_uri: str = Field(default="mongodb://127.0.0.1:27017")
    mongo_database: str = Field(default="hackson")
    jwt_secret: str = Field(default="dev-only-change-me-with-at-least-32-bytes")
    jwt_algorithm: str = Field(default="HS256")
    access_token_minutes: int = Field(default=60 * 24)
    static_frontend_dir: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
