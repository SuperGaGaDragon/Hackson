"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from context.packages import build_context_package
from context.schemas import ContextMode, ModelMessage
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse
from orchestration.schemas import OrchestrationRequest
from orchestration.service import HacksonOrchestrator


class FakeModelRuntime:
    def __init__(self) -> None:
        self.requests: list[ModelGenerateRequest] = []

    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse:
        self.requests.append(request)
        return ModelGenerateResponse(
            text="orchestrated reply",
            model_name="fake-responses-model",
            provider="fake",
            provider_response_id="resp_fake",
            reasoning_summary="safe summary",
        )


class HacksonOrchestratorTest(TestCase):
    def test_generates_with_mode_policy_and_context_messages(self) -> None:
        runtime = FakeModelRuntime()
        orchestrator = HacksonOrchestrator(runtime)
        package = build_context_package(
            mode=ContextMode.COMPANION_2,
            conversation_id="conv_1",
            agent_id="agent_1",
            messages=[
                ModelMessage(role="system", content="system policy"),
                ModelMessage(role="user", content="Current mode: companion_2"),
            ],
            included_message_ids=["msg_1"],
            included_summary_ids=[],
            included_agent_ids=["agent_1"],
        )

        response = orchestrator.generate(
            OrchestrationRequest(
                mode=ContextMode.COMPANION_2,
                user_id="user_1",
                conversation_id="conv_1",
                target_agent_id="agent_1",
                context_package=package,
            )
        )

        self.assertEqual(response.text, "orchestrated reply")
        self.assertEqual(response.model_name, "fake-responses-model")
        self.assertEqual(response.provider_response_id, "resp_fake")
        self.assertEqual(response.policy_name, "companion_chat_quality_v1")
        self.assertEqual(response.reasoning_effort, "medium")
        self.assertEqual(response.metadata["prompt_hash"], package.prompt_hash)
        self.assertEqual(response.metadata["included_message_ids"], ["msg_1"])
        self.assertEqual(len(runtime.requests), 1)
        runtime_request = runtime.requests[0]
        self.assertEqual(runtime_request.max_output_tokens, 700)
        self.assertEqual(runtime_request.temperature, 0.5)
        self.assertEqual(runtime_request.reasoning_effort, "medium")
        self.assertEqual(runtime_request.tool_policy, "disabled")
        self.assertEqual(runtime_request.metadata["orchestration_policy"], "companion_chat_quality_v1")
        self.assertEqual(runtime_request.messages[1].content, "Current mode: companion_2")

    def test_idle_request_uses_conservative_policy(self) -> None:
        runtime = FakeModelRuntime()
        orchestrator = HacksonOrchestrator(runtime)
        package = build_context_package(
            mode=ContextMode.IDLE,
            conversation_id="idle_1",
            agent_id="agent_2",
            messages=[ModelMessage(role="user", content="Current mode: idle")],
            included_message_ids=[],
            included_summary_ids=[],
            included_agent_ids=["agent_2"],
        )

        orchestrator.generate(
            OrchestrationRequest(
                mode=ContextMode.IDLE,
                user_id="user_1",
                conversation_id="idle_1",
                target_agent_id="agent_2",
                context_package=package,
            )
        )

        runtime_request = runtime.requests[0]
        self.assertEqual(runtime_request.max_output_tokens, 360)
        self.assertEqual(runtime_request.reasoning_effort, "low")
        self.assertEqual(runtime_request.tool_policy, "disabled")
