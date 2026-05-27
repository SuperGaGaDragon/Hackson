"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse
from work_mode.action_client import DelegateResultClient, ToolActionClient, ToolActionClientError


class WorkModeActionClientTest(TestCase):
    def test_generates_one_tool_action_from_model_runtime(self) -> None:
        runtime = FakeModelRuntime(
            """
            {
              "tool": "mission_plan",
              "arguments": {
                "reason": "先规划。",
                "planTitle": "小说计划",
                "steps": [{"title": "写大纲", "status": "pending", "notes": ""}]
              }
            }
            """
        )
        client = ToolActionClient(runtime)

        action = client.generate_action({"mission": {"goal": "写小说"}})

        self.assertEqual(action.tool, "mission_plan")
        self.assertEqual(runtime.last_request.reasoning_effort, "low")
        self.assertIn("Return exactly one JSON tool action", runtime.last_request.messages[0].content)

    def test_invalid_model_text_raises_client_error(self) -> None:
        client = ToolActionClient(FakeModelRuntime("我先写一个大纲。"))

        with self.assertRaises(ToolActionClientError) as error:
            client.generate_action({"mission": {"goal": "写小说"}})

        self.assertEqual(error.exception.code, "tool_action_invalid_json")

    def test_provider_timeout_maps_to_retryable_error(self) -> None:
        client = ToolActionClient(FakeModelRuntime(error=ModelRuntimeError("model_timeout")))

        with self.assertRaises(ToolActionClientError) as error:
            client.generate_action({"mission": {"goal": "写小说"}})

        self.assertEqual(error.exception.code, "model_timeout")
        self.assertTrue(error.exception.retryable)

    def test_http_429_maps_to_retryable_error(self) -> None:
        client = ToolActionClient(FakeModelRuntime(error=ModelRuntimeError("model_http_error:429", http_status=429)))

        with self.assertRaises(ToolActionClientError) as error:
            client.generate_action({"mission": {"goal": "写小说"}})

        self.assertEqual(error.exception.code, "model_http_error:429")
        self.assertTrue(error.exception.retryable)

    def test_delegate_result_client_requests_structured_json(self) -> None:
        runtime = FakeModelRuntime(
            """
            {"status":"completed","title":"第一章","summary":"完成。","content":"正文","reason":"按 brief 完成。"}
            """
        )
        client = DelegateResultClient(runtime)

        result = client.generate_delegate_result({"brief": "写第一章。"})

        self.assertIn('"status":"completed"', result)
        self.assertEqual(runtime.last_request.max_output_tokens, 3000)
        self.assertIn("Return exactly one JSON object", runtime.last_request.messages[0].content)
        self.assertIn("Do not call tools", runtime.last_request.messages[0].content)


class FakeModelRuntime:
    def __init__(self, text: str = "", error: Exception | None = None):
        self.text = text
        self.error = error
        self.last_request: ModelGenerateRequest | None = None

    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse:
        self.last_request = request
        if self.error:
            raise self.error
        return ModelGenerateResponse(text=self.text, model_name="fake-model", provider="fake")
