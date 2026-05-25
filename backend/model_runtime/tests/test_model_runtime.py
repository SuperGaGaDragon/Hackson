"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

import os
from unittest import TestCase
from unittest.mock import patch

from model_runtime.client import _chat_completions_url, _extract_text
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, ModelRuntimeConfig, RuntimeMessage


class FakeClient:
    def __init__(self) -> None:
        self.last_config: ModelRuntimeConfig | None = None
        self.last_request: ModelGenerateRequest | None = None

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> str:
        self.last_config = config
        self.last_request = request
        return "本地模型运行层回复"


class ModelRuntimeTest(TestCase):
    def test_config_prefers_hackson_model_env(self) -> None:
        env = {
            "HACKSON_MODEL_API_KEY": "secret-hackson",
            "HACKSON_MODEL_BASE_URL": "https://codex-relay.example.com/v1",
            "HACKSON_MODEL_NAME": "codex-relay-model",
            "OPENAI_API_KEY": "secret-openai",
            "STYLE_REPORT_MODEL": "fallback-model",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ModelRuntimeConfigRepository(env_file=None).get_enabled_config()

        self.assertEqual(config.base_url, "https://codex-relay.example.com/v1")
        self.assertEqual(config.model_name, "codex-relay-model")
        self.assertEqual(config.api_key, "secret-hackson")

    def test_config_falls_back_to_codex_openai_compatible_env(self) -> None:
        env = {
            "OPENAI_API_KEY": "secret-openai",
            "STYLE_REPORT_MODEL": "gpt-5.1",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ModelRuntimeConfigRepository(env_file=None).get_enabled_config()

        self.assertEqual(config.base_url, "https://api.openai.com/v1")
        self.assertEqual(config.model_name, "gpt-5.1")
        self.assertEqual(config.api_key, "secret-openai")

    def test_orchestrator_returns_normalized_response_without_exposing_secret(self) -> None:
        fake_client = FakeClient()
        runtime = ModelRuntime(
            config_repository=StaticConfigRepository(),
            client=fake_client,
        )
        response = runtime.generate(
            ModelGenerateRequest(
                messages=[RuntimeMessage(role="user", content="hello")],
            )
        )

        self.assertEqual(response.text, "本地模型运行层回复")
        self.assertEqual(response.model_name, "codex-test-model")
        self.assertNotIn("secret", response.model_dump_json())
        self.assertIsNotNone(fake_client.last_request)

    def test_chat_completions_url_normalizes_base_url(self) -> None:
        self.assertEqual(
            _chat_completions_url("https://relay.example.com/v1"),
            "https://relay.example.com/v1/chat/completions",
        )
        self.assertEqual(
            _chat_completions_url("https://relay.example.com/v1/chat/completions"),
            "https://relay.example.com/v1/chat/completions",
        )

    def test_extract_text_from_openai_compatible_response(self) -> None:
        text = _extract_text({"choices": [{"message": {"content": "hello"}}]})
        self.assertEqual(text, "hello")


class StaticConfigRepository:
    def get_enabled_config(self) -> ModelRuntimeConfig:
        return ModelRuntimeConfig(
            base_url="https://relay.example.com/v1",
            model_name="codex-test-model",
            api_key="secret-token",
        )
