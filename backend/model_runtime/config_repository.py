"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from model_runtime.schemas import ModelRuntimeConfig


DEFAULT_OPENAI_COMPATIBLE_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL_NAME = "gpt-5.1"


class ModelEnvSettings(BaseSettings):
    """Platform model settings loaded from local .env or process env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HACKSON_MODEL_", extra="ignore")

    api_key: str | None = None
    base_url: str | None = None
    name: str | None = None
    timeout_seconds: float | None = None
    max_output_tokens: int | None = None
    temperature: float | None = None


class ModelRuntimeConfigRepository:
    """Read platform-managed model config from local environment only."""

    def __init__(self, env_file: str | None = ".env"):
        self.env_file = env_file

    def get_enabled_config(self) -> ModelRuntimeConfig:
        settings = ModelEnvSettings(_env_file=self.env_file)
        api_key = settings.api_key or _first_env("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("model_api_key_missing")

        return ModelRuntimeConfig(
            base_url=settings.base_url or _first_env("OPENAI_BASE_URL") or DEFAULT_OPENAI_COMPATIBLE_BASE_URL,
            model_name=settings.name or _first_env("STYLE_REPORT_MODEL") or DEFAULT_MODEL_NAME,
            api_key=api_key,
            timeout_seconds=settings.timeout_seconds or 60,
            max_output_tokens=settings.max_output_tokens or 1024,
            temperature=settings.temperature or 0.7,
        )


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None
