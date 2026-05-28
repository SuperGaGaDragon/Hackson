"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import os
import signal
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, patch

from model_runtime.client import (
    CodexCliClient,
    OpenAICompatibleClient,
    OpenAIResponsesClient,
    _codex_command,
    _codex_prompt,
    _codex_reasoning_effort,
    _run_codex_subprocess,
    _chat_completions_url,
    _extract_reasoning_summary,
    _extract_response_text,
    _extract_text,
    _responses_url,
)
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.errors import ModelRuntimeError
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, ModelRuntimeConfig, RuntimeMessage


class FakeClient:
    def __init__(self) -> None:
        self.last_config: ModelRuntimeConfig | None = None
        self.last_request: ModelGenerateRequest | None = None

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse:
        self.last_config = config
        self.last_request = request
        return ModelGenerateResponse(text="本地模型运行层回复", model_name=config.model_name, provider=config.provider)


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
        self.assertEqual(config.api_mode, "chat_completions")

    def test_config_can_enable_responses_mode(self) -> None:
        env = {
            "OPENAI_API_KEY": "secret-openai",
            "HACKSON_MODEL_API_MODE": "responses",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ModelRuntimeConfigRepository(env_file=None).get_enabled_config()

        self.assertEqual(config.api_mode, "responses")

    def test_config_can_enable_codex_cli_provider_without_openai_key(self) -> None:
        env = {
            "HACKSON_MODEL_PROVIDER": "codex_cli",
            "HACKSON_MODEL_NAME": "gpt-5.4",
            "HACKSON_MODEL_CODEX_COMMAND": "/usr/local/bin/codex",
            "HACKSON_MODEL_CODEX_HOME": "/home/catadragon/.codex",
        }
        with patch.dict(os.environ, env, clear=True):
            config = ModelRuntimeConfigRepository(env_file=None).get_enabled_config()

        self.assertEqual(config.provider, "codex_cli")
        self.assertEqual(config.model_name, "gpt-5.4")
        self.assertEqual(config.codex_command, "/usr/local/bin/codex")
        self.assertEqual(config.codex_home, "/home/catadragon/.codex")
        self.assertNotIn("codex-cli-auth", config.model_dump_json())

    def test_config_reads_explicit_env_file(self) -> None:
        with TemporaryDirectory() as directory:
            env_file = Path(directory) / "model.env"
            env_file.write_text(
                "OPENAI_API_KEY=secret-file\nSTYLE_REPORT_MODEL=file-model\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                config = ModelRuntimeConfigRepository(env_file=str(env_file)).get_enabled_config()

        self.assertEqual(config.model_name, "file-model")
        self.assertEqual(config.api_key, "secret-file")

    def test_missing_model_api_key_raises_structured_runtime_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ModelRuntimeError) as error:
                ModelRuntimeConfigRepository(env_file=None).get_enabled_config()

        self.assertEqual(error.exception.code, "model_api_key_missing")

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

    def test_orchestrator_uses_responses_client_when_enabled(self) -> None:
        chat_client = FakeClient()
        responses_client = FakeClient()
        runtime = ModelRuntime(
            config_repository=StaticConfigRepository(api_mode="responses"),
            client=chat_client,
            responses_client=responses_client,
        )

        runtime.generate(ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")]))

        self.assertIsNone(chat_client.last_request)
        self.assertIsNotNone(responses_client.last_request)

    def test_orchestrator_uses_codex_cli_client_when_provider_enabled(self) -> None:
        chat_client = FakeClient()
        codex_client = FakeClient()
        runtime = ModelRuntime(
            config_repository=StaticConfigRepository(provider="codex_cli"),
            client=chat_client,
            codex_cli_client=codex_client,
        )

        response = runtime.generate(ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")]))

        self.assertEqual(response.provider, "codex_cli")
        self.assertIsNone(chat_client.last_request)
        self.assertIsNotNone(codex_client.last_request)

    def test_request_can_force_responses_client(self) -> None:
        chat_client = FakeClient()
        responses_client = FakeClient()
        runtime = ModelRuntime(
            config_repository=StaticConfigRepository(api_mode="chat_completions"),
            client=chat_client,
            responses_client=responses_client,
        )

        runtime.generate(
            ModelGenerateRequest(
                messages=[RuntimeMessage(role="user", content="hello")],
                use_responses_api=True,
            )
        )

        self.assertIsNone(chat_client.last_request)
        self.assertIsNotNone(responses_client.last_request)

    def test_chat_completions_url_normalizes_base_url(self) -> None:
        self.assertEqual(
            _chat_completions_url("https://relay.example.com/v1"),
            "https://relay.example.com/v1/chat/completions",
        )

    def test_responses_url_normalizes_base_url(self) -> None:
        self.assertEqual(_responses_url("https://relay.example.com/v1"), "https://relay.example.com/v1/responses")
        self.assertEqual(
            _responses_url("https://relay.example.com/v1/responses"),
            "https://relay.example.com/v1/responses",
        )
        self.assertEqual(
            _chat_completions_url("https://relay.example.com/v1/chat/completions"),
            "https://relay.example.com/v1/chat/completions",
        )

    def test_extract_text_from_openai_compatible_response(self) -> None:
        text = _extract_text({"choices": [{"message": {"content": "hello"}}]})
        self.assertEqual(text, "hello")

    def test_extract_response_text_from_output_text(self) -> None:
        text = _extract_response_text({"output_text": "hello responses"})
        self.assertEqual(text, "hello responses")

    def test_extract_response_text_from_output_items(self) -> None:
        text = _extract_response_text(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "hello"},
                            {"type": "output_text", "text": " world"},
                        ],
                    }
                ]
            }
        )
        self.assertEqual(text, "hello world")

    def test_extract_reasoning_summary_from_output_items(self) -> None:
        summary = _extract_reasoning_summary(
            {
                "output": [
                    {
                        "type": "reasoning",
                        "summary": [{"type": "summary_text", "text": "safe summary"}],
                    }
                ]
            }
        )
        self.assertEqual(summary, "safe summary")

    def test_extract_text_raises_structured_runtime_error(self) -> None:
        with self.assertRaises(ModelRuntimeError) as error:
            _extract_text({"choices": []})

        self.assertEqual(error.exception.code, "model_response_missing_choices")

    def test_http_error_maps_to_structured_runtime_error(self) -> None:
        client = OpenAICompatibleClient()
        with patch("model_runtime.client.urlopen") as fake_urlopen:
            from urllib.error import HTTPError

            fake_urlopen.side_effect = HTTPError(
                url="https://relay.example.com/v1/chat/completions",
                code=429,
                msg="Too Many Requests",
                hdrs=None,
                fp=None,
            )

            with self.assertRaises(ModelRuntimeError) as error:
                client.generate(
                    StaticConfigRepository().get_enabled_config(),
                    ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")]),
                )

        self.assertEqual(error.exception.code, "model_http_error:429")
        self.assertEqual(error.exception.http_status, 429)

    def test_openai_compatible_client_uses_request_timeout_override(self) -> None:
        client = OpenAICompatibleClient()
        with patch.object(client, "_post_json", return_value={"id": "chat_1", "model": "gpt-test", "choices": [{"message": {"content": "hello"}}]}) as fake_post:
            client.generate(
                StaticConfigRepository().get_enabled_config(),
                ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")], timeout_seconds=12),
            )

        self.assertEqual(fake_post.call_args.args[3], 12)

    def test_responses_client_builds_reasoning_payload_and_normalizes_response(self) -> None:
        client = OpenAIResponsesClient()
        fake_response = FakeHTTPXResponse(
            {
                "id": "resp_123",
                "model": "gpt-test",
                "output_text": "hello",
                "output": [{"type": "reasoning", "summary": ["safe summary"]}],
            }
        )
        with patch("model_runtime.client.httpx.post", return_value=fake_response) as fake_post:
            response = client.generate(
                StaticConfigRepository(api_mode="responses").get_enabled_config(),
                ModelGenerateRequest(
                    messages=[RuntimeMessage(role="user", content="hello")],
                    reasoning_effort="medium",
                    tool_policy="disabled",
                ),
            )

        payload = fake_post.call_args.kwargs["json"]
        self.assertEqual(payload["reasoning"]["effort"], "medium")
        self.assertEqual(payload["reasoning"]["summary"], "auto")
        self.assertNotIn("tools", payload)
        self.assertEqual(response.text, "hello")
        self.assertEqual(response.provider_response_id, "resp_123")
        self.assertEqual(response.reasoning_summary, "safe summary")

    def test_responses_client_uses_request_timeout_override(self) -> None:
        client = OpenAIResponsesClient()
        with patch.object(client, "_post_json", return_value={"id": "resp_1", "model": "gpt-test", "output_text": "hello"}) as fake_post:
            client.generate(
                StaticConfigRepository(api_mode="responses").get_enabled_config(),
                ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")], timeout_seconds=34),
            )

        self.assertEqual(fake_post.call_args.args[3], 34)

    def test_codex_cli_command_is_ephemeral_read_only_and_non_interactive(self) -> None:
        request = ModelGenerateRequest(
            messages=[RuntimeMessage(role="user", content="hello")],
            reasoning_effort="minimal",
        )
        config = StaticConfigRepository(provider="codex_cli").get_enabled_config()

        command = _codex_command(config, request, "/tmp/work", "/tmp/out")

        self.assertIn("exec", command)
        self.assertIn("--ephemeral", command)
        self.assertIn("--ignore-rules", command)
        self.assertIn("approval_policy=never", command)
        self.assertIn("model_reasoning_effort=low", command)
        self.assertIn("-", command)

    def test_codex_prompt_preserves_runtime_messages(self) -> None:
        prompt = _codex_prompt(
            ModelGenerateRequest(
                messages=[
                    RuntimeMessage(role="system", content="system prompt"),
                    RuntimeMessage(role="user", content="hello"),
                ]
            )
        )

        self.assertIn("[system]\nsystem prompt", prompt)
        self.assertIn("[user]\nhello", prompt)

    def test_codex_client_normalizes_last_message_output(self) -> None:
        config = StaticConfigRepository(provider="codex_cli").get_enabled_config()
        request = ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")])

        def fake_popen(command, stdin, stdout, stderr, text, start_new_session, env):
            output_path = command[command.index("-o") + 1]
            Path(output_path).write_text("codex reply\n", encoding="utf-8")
            return FakePopen(stdout_text="ignored stdout")

        with patch("model_runtime.client.subprocess.Popen", side_effect=fake_popen):
            response = CodexCliClient().generate(config, request)

        self.assertEqual(response.text, "codex reply")
        self.assertEqual(response.model_name, "codex-test-model")
        self.assertEqual(response.provider, "codex_cli")

    def test_codex_client_uses_request_timeout_override(self) -> None:
        config = StaticConfigRepository(provider="codex_cli").get_enabled_config()
        request = ModelGenerateRequest(messages=[RuntimeMessage(role="user", content="hello")], timeout_seconds=56)

        def fake_run(command, input, timeout_seconds, env):
            output_path = command[command.index("-o") + 1]
            Path(output_path).write_text("codex reply\n", encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

        with patch("model_runtime.client._run_codex_subprocess", side_effect=fake_run) as fake_subprocess:
            response = CodexCliClient().generate(config, request)

        self.assertEqual(response.text, "codex reply")
        self.assertEqual(fake_subprocess.call_args.kwargs["timeout_seconds"], 56)

    def test_codex_subprocess_success_cleans_process_group(self) -> None:
        process = FakePopen(stdout_text="codex reply")
        with patch("model_runtime.client.subprocess.Popen", return_value=process):
            with patch("model_runtime.client.os.killpg") as fake_killpg:
                result = _run_codex_subprocess(["codex"], "prompt", timeout_seconds=1, env={})

        self.assertEqual(result.stdout, "codex reply")
        fake_killpg.assert_called_once_with(process.pid, signal.SIGTERM)
        self.assertTrue(process.wait_called)

    def test_codex_subprocess_timeout_kills_process_group(self) -> None:
        process = TimeoutPopen(wait_timeouts=1)
        with patch("model_runtime.client.subprocess.Popen", return_value=process):
            with patch("model_runtime.client.os.killpg") as fake_killpg:
                with self.assertRaises(subprocess.TimeoutExpired):
                    _run_codex_subprocess(["codex"], "prompt", timeout_seconds=1, env={})

        self.assertEqual(
            fake_killpg.call_args_list,
            [call(process.pid, signal.SIGTERM), call(process.pid, signal.SIGKILL)],
        )
        self.assertTrue(process.wait_called)

    def test_codex_reasoning_maps_minimal_to_low(self) -> None:
        self.assertEqual(_codex_reasoning_effort("minimal"), "low")
        self.assertEqual(_codex_reasoning_effort("high"), "high")
        self.assertEqual(_codex_reasoning_effort(None), "medium")


class FakeHTTPXResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakePopen:
    def __init__(self, returncode: int = 0, stdout_text: str = "", stderr_text: str = ""):
        self.pid = 12345
        self.returncode = returncode
        self.stdout_text = stdout_text
        self.stderr_text = stderr_text
        self.wait_called = False

    def communicate(self, input: str, timeout: float):
        return self.stdout_text, self.stderr_text

    def wait(self, timeout: float | None = None) -> int:
        self.wait_called = True
        return self.returncode


class TimeoutPopen:
    def __init__(self, wait_timeouts: int = 0):
        self.pid = 54321
        self.wait_called = False
        self.wait_timeouts = wait_timeouts

    def communicate(self, input: str, timeout: float):
        raise subprocess.TimeoutExpired(cmd="codex", timeout=timeout)

    def wait(self, timeout: float | None = None) -> int:
        self.wait_called = True
        if self.wait_timeouts > 0:
            self.wait_timeouts -= 1
            raise subprocess.TimeoutExpired(cmd="codex", timeout=timeout)
        return -signal.SIGTERM


class StaticConfigRepository:
    def __init__(self, api_mode: str = "chat_completions", provider: str = "openai_compatible"):
        self.api_mode = api_mode
        self.provider = provider

    def get_enabled_config(self) -> ModelRuntimeConfig:
        return ModelRuntimeConfig(
            provider=self.provider,
            base_url="https://relay.example.com/v1",
            model_name="codex-test-model",
            api_key="secret-token",
            api_mode=self.api_mode,
            codex_command="/usr/local/bin/codex",
            codex_home="/home/catadragon/.codex",
        )
