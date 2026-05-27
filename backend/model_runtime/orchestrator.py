"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Protocol

from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, ModelRuntimeConfig


class ModelClientProtocol(Protocol):
    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse: ...


class ModelRuntime:
    """Uniform model generation entrypoint for backend callers."""

    def __init__(
        self,
        config_repository: ModelRuntimeConfigRepository,
        client: ModelClientProtocol,
        responses_client: ModelClientProtocol | None = None,
        codex_cli_client: ModelClientProtocol | None = None,
    ):
        self.config_repository = config_repository
        self.client = client
        self.responses_client = responses_client
        self.codex_cli_client = codex_cli_client

    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse:
        config = self.config_repository.get_enabled_config()
        client = self._client_for(config, request)
        response = client.generate(config, request)
        if not response.model_name:
            response.model_name = config.model_name
        if not response.provider:
            response.provider = config.provider
        return response

    def _client_for(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelClientProtocol:
        if config.provider == "codex_cli":
            if self.codex_cli_client is None:
                raise ModelRuntimeError("model_codex_cli_unavailable")
            return self.codex_cli_client
        use_responses = request.use_responses_api if request.use_responses_api is not None else config.api_mode == "responses"
        if use_responses and self.responses_client is not None:
            return self.responses_client
        return self.client
