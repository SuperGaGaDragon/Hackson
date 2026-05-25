"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Protocol

from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, ModelRuntimeConfig


class ModelClientProtocol(Protocol):
    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> str: ...


class ModelRuntime:
    """Uniform model generation entrypoint for backend callers."""

    def __init__(
        self,
        config_repository: ModelRuntimeConfigRepository,
        client: ModelClientProtocol,
    ):
        self.config_repository = config_repository
        self.client = client

    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse:
        config = self.config_repository.get_enabled_config()
        text = self.client.generate(config, request)
        return ModelGenerateResponse(
            text=text,
            model_name=config.model_name,
            provider=config.provider,
        )

