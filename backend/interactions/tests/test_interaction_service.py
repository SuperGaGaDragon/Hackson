"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.tests.test_conversation_service import FakeConversationRepository
from conversations.service import ConversationService
from context.builder import ContextBuilder
from interactions.schemas import IdleTickRequest, InteractionUserMessageRequest
from interactions.service import InteractionService
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse


class FakeModelRuntime:
    def __init__(self) -> None:
        self.requests: list[ModelGenerateRequest] = []

    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse:
        self.requests.append(request)
        prompt = "\n".join(message.content for message in request.messages)
        if "companion_1" in prompt:
            text = "我看到你加入了，我们刚才在聊 idle 生活是否需要目标。"
        elif "companion_2" in prompt:
            text = "Hackson V1 先跑通稳定实用的双 Agent 对话体验。"
        else:
            text = "那我们继续把这个 idle 想法讲清楚。"
        return ModelGenerateResponse(text=text, model_name="fake-model", provider="fake")


class InteractionServiceTest(TestCase):
    def setUp(self) -> None:
        self.conversation_service = ConversationService(FakeConversationRepository())
        self.model_runtime = FakeModelRuntime()
        self.service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
        )

    def test_idle_tick_saves_agent_reply_with_context_metadata(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        self.conversation_service.append_message(
            "user_1",
            idle["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="今天要不要继续讨论目标感？",
            ),
        )

        response = self.service.run_idle_tick("user_1", idle["id"], IdleTickRequest())

        self.assertEqual(response["conversation"]["mode"], "idle")
        self.assertEqual(response["conversation"]["messageCount"], 2)
        self.assertEqual(response["agentMessage"]["senderType"], "agent")
        self.assertEqual(response["agentMessage"]["sequence"], 2)
        self.assertIn("promptHash", response["context"])
        self.assertEqual(len(self.model_runtime.requests), 1)

    def test_companion_1_join_creates_child_conversation_and_transition_reply(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        self.conversation_service.append_message(
            "user_1",
            idle["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="目标感会不会破坏 idle？",
            ),
        )

        response = self.service.run_companion_1_join(
            "user_1",
            idle["id"],
            InteractionUserMessageRequest(content="我可以加入吗？"),
        )

        self.assertEqual(response["conversation"]["mode"], "companion_1")
        self.assertEqual(response["conversation"]["parentConversationId"], idle["id"])
        self.assertEqual(response["conversation"]["messageCount"], 2)
        self.assertEqual(response["userMessage"]["senderType"], "user")
        self.assertEqual(response["agentMessage"]["sequence"], 2)
        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("用户刚刚加入", prompt)
        self.assertIn("我可以加入吗？", prompt)

    def test_companion_2_message_saves_user_and_agent_messages(self) -> None:
        companion = self.conversation_service.create_conversation(
            "user_1",
            ConversationCreateRequest(mode="companion_2"),
        )

        response = self.service.run_companion_2_message(
            "user_1",
            companion["id"],
            InteractionUserMessageRequest(content="一句话说 V1 目标。", targetAgentId="agent_2"),
        )

        self.assertEqual(response["conversation"]["mode"], "companion_2")
        self.assertEqual(response["conversation"]["messageCount"], 2)
        self.assertEqual(response["userMessage"]["sequence"], 1)
        self.assertEqual(response["agentMessage"]["sequence"], 2)
        self.assertEqual(response["agentMessage"]["senderSlot"], "agent_2")
        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("Current mode: companion_2", prompt)
        self.assertIn("一句话说 V1 目标", prompt)
        self.assertIn("name: Vale", prompt)
        self.assertNotIn("name: Beryl", prompt)


def _prompt_text(request: ModelGenerateRequest) -> str:
    return "\n".join(message.content for message in request.messages)
