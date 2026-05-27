"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import os
from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings, SettingsConfigDict

from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelRuntimeConfig


DEFAULT_OPENAI_COMPATIBLE_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL_NAME = "gpt-5.1"


class ModelEnvSettings(BaseSettings):
    """Platform model settings loaded from local .env or process env."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="HACKSON_MODEL_", extra="ignore")

    api_key: str | None = None
    base_url: str | None = None
    name: str | None = None
    api_mode: str | None = None
    responses_enabled: bool | None = None
    timeout_seconds: float | None = None
    max_output_tokens: int | None = None
    temperature: float | None = None


class ModelRuntimeConfigRepository:
    """Read platform-managed model config from local environment only."""

    def __init__(self, env_file: str | None | tuple[str, ...] = ".env"):
        self.env_file = env_file

    def get_enabled_config(self) -> ModelRuntimeConfig:
        env_file = _resolve_env_file(self.env_file)
        env_values = _env_file_values(env_file)
        settings = ModelEnvSettings(_env_file=env_file)
        api_key = settings.api_key or _first_config_value(env_values, "OPENAI_API_KEY")
        if not api_key:
            raise ModelRuntimeError("model_api_key_missing")

        return ModelRuntimeConfig(
            base_url=settings.base_url
            or _first_config_value(env_values, "OPENAI_BASE_URL")
            or DEFAULT_OPENAI_COMPATIBLE_BASE_URL,
            model_name=settings.name or _first_config_value(env_values, "STYLE_REPORT_MODEL") or DEFAULT_MODEL_NAME,
            api_key=api_key,
            api_mode=_api_mode(settings, env_values),
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


def _first_config_value(env_values: dict[str, str | None], *names: str) -> str | None:
    for name in names:
        value = os.getenv(name) or env_values.get(name)
        if value:
            return value
    return None


def _env_file_values(env_file: str | tuple[str, ...] | None) -> dict[str, str | None]:
    values: dict[str, str | None] = {}
    if env_file is None:
        return values

    files = (env_file,) if isinstance(env_file, str) else env_file
    for file_name in files:
        path = Path(file_name)
        if path.is_file():
            values.update(dotenv_values(path))
    return values


def _resolve_env_file(env_file: str | tuple[str, ...] | None) -> str | tuple[str, ...] | None:
    if env_file != ".env":
        return env_file

    candidates = (
        Path(".env"),
        Path("../.env"),
        Path.home() / ".env",
    )
    existing = tuple(str(path) for path in candidates if path.is_file())
    return existing or ".env"


def _api_mode(settings: ModelEnvSettings, env_values: dict[str, str | None]) -> str:
    explicit_mode = settings.api_mode or _first_config_value(env_values, "HACKSON_MODEL_API_MODE")
    if explicit_mode:
        mode = explicit_mode.strip().lower()
        if mode in {"responses", "chat_completions"}:
            return mode
    responses_enabled = settings.responses_enabled
    if responses_enabled is None:
        raw = _first_config_value(env_values, "HACKSON_MODEL_RESPONSES_ENABLED")
        responses_enabled = raw.strip().lower() in {"1", "true", "yes", "on"} if raw else False
    return "responses" if responses_enabled else "chat_completions"
