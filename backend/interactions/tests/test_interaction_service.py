"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
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
from workers.tests.test_derived_jobs import FakeDerivedJobRepository
from workers.derived_jobs import DerivedJobService


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


class FakeUserService:
    def __init__(self, users: dict[str, dict[str, Any]] | None = None) -> None:
        self.users = users or {}

    def get_user(self, user_id: str) -> dict[str, Any]:
        return self.users.get(
            user_id,
            {
                "id": user_id,
                "username": "demo_user",
                "displayName": "Demo",
                "languagePreference": "zh",
                "personality": "",
                "story": "",
                "agentProfiles": [],
            },
        )


class InteractionServiceTest(TestCase):
    def setUp(self) -> None:
        self.conversation_service = ConversationService(FakeConversationRepository())
        self.model_runtime = FakeModelRuntime()
        self.service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            derived_jobs=DerivedJobService(FakeDerivedJobRepository()),
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

    def test_idle_tick_uses_latest_recent_messages_after_long_history(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        for index in range(25):
            slot = "agent_1" if index % 2 == 0 else "agent_2"
            self.conversation_service.append_message(
                "user_1",
                idle["id"],
                MessageAppendRequest(
                    sender_type="agent",
                    sender_slot=slot,
                    role="assistant",
                    content=f"old loop marker {index}",
                ),
            )
        self.conversation_service.append_message(
            "user_1",
            idle["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="fresh anti-repeat marker",
            ),
        )

        self.service.run_idle_tick("user_1", idle["id"], IdleTickRequest(targetAgentId="agent_1"))

        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("fresh anti-repeat marker", prompt)
        recent_section = prompt.split("Recent Nora/Vale idle messages:", maxsplit=1)[1]
        self.assertNotIn("old loop marker 0", recent_section)
        self.assertIn("Vale:", prompt)

    def test_idle_tick_passes_user_profile_direction_and_compact_summary(self) -> None:
        user_service = FakeUserService(
            {
                "user_1": {
                    "id": "user_1",
                    "username": "demo_user",
                    "displayName": "Demo",
                    "languagePreference": "zh",
                    "personality": "quiet, direct, product-minded",
                    "story": "I am preparing a 30 second demo.",
                    "agentProfiles": [
                        {
                            "slot": "agent_1",
                            "name": "Mira",
                            "short": "A1",
                            "color": "teal",
                            "voice": "soft skeptic",
                            "personality": "A careful skeptic who spots demo risk.",
                            "story": "Used to be Nora, now focused on launch narrative.",
                        },
                        {
                            "slot": "agent_2",
                            "name": "Rook",
                            "short": "A2",
                            "color": "amber",
                            "voice": "direct builder",
                            "personality": "A builder who converts ideas into next steps.",
                            "story": "",
                        },
                    ],
                }
            }
        )
        service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            user_service=user_service,
        )
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        for index in range(30):
            slot = "agent_1" if index % 2 == 0 else "agent_2"
            self.conversation_service.append_message(
                "user_1",
                idle["id"],
                MessageAppendRequest(
                    sender_type="agent",
                    sender_slot=slot,
                    role="assistant",
                    content=f"older context marker {index}",
                ),
            )
        self.conversation_service.append_message(
            "user_1",
            idle["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="latest visible topic marker",
            ),
        )

        response = service.run_idle_tick(
            "user_1",
            idle["id"],
            IdleTickRequest(targetAgentId="agent_1", discussionDirection="希望从 demo 讲解节奏展开"),
        )

        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("User profile:", prompt)
        self.assertIn("name: Mira", prompt)
        self.assertIn("core_persona: A careful skeptic who spots demo risk.", prompt)
        self.assertIn("- Rook: A builder who converts ideas into next steps.", prompt)
        self.assertIn("personality: quiet, direct, product-minded", prompt)
        self.assertIn("story: I am preparing a 30 second demo.", prompt)
        self.assertIn("User direction:", prompt)
        self.assertIn("希望从 demo 讲解节奏展开", prompt)
        self.assertIn("compact_context summary:", prompt)
        self.assertIn("older context marker 0", prompt)
        self.assertIn("latest visible topic marker", prompt)
        self.assertEqual(response["conversation"]["messageCount"], 32)
        page = self.conversation_service.list_messages(
            "user_1",
            idle["id"],
            after_sequence=0,
            created_after=None,
            created_before=None,
            limit=100,
        )
        self.assertFalse(any(message["senderType"] == "user" for message in page["messages"]))

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

    def test_companion_1_child_accepts_followup_message(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        joined = self.service.run_companion_1_join(
            "user_1",
            idle["id"],
            InteractionUserMessageRequest(content="我加入聊这个话题。"),
        )

        response = self.service.run_companion_message(
            "user_1",
            joined["conversation"]["id"],
            InteractionUserMessageRequest(content="继续解释一下。", targetAgentId="agent_2"),
        )

        self.assertEqual(response["conversation"]["mode"], "companion_1")
        self.assertEqual(response["conversation"]["parentConversationId"], idle["id"])
        self.assertEqual(response["conversation"]["messageCount"], 4)
        self.assertEqual(response["userMessage"]["sequence"], 3)
        self.assertEqual(response["agentMessage"]["sequence"], 4)
        self.assertEqual(response["agentMessage"]["senderSlot"], "agent_2")
        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("Current mode: companion_1", prompt)
        self.assertIn("继续解释一下。", prompt)

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

    def test_companion_2_context_uses_current_user_profile(self) -> None:
        user_service = FakeUserService(
            {
                "user_1": {
                    "id": "user_1",
                    "username": "demo_user",
                    "displayName": "Demo",
                    "languagePreference": "zh",
                    "personality": "skeptical but fast-moving",
                    "story": "I am testing whether the product respects user background.",
                    "agentProfiles": [
                        {
                            "slot": "agent_1",
                            "name": "Mira",
                            "short": "A1",
                            "color": "teal",
                            "voice": "careful",
                            "personality": "A careful skeptic.",
                            "story": "",
                        },
                        {
                            "slot": "agent_2",
                            "name": "Rook",
                            "short": "A2",
                            "color": "amber",
                            "voice": "builder",
                            "personality": "A product builder.",
                            "story": "Works fast.",
                        },
                    ],
                }
            }
        )
        service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            user_service=user_service,
        )
        companion = self.conversation_service.create_conversation(
            "user_1",
            ConversationCreateRequest(mode="companion_2"),
        )

        service.run_companion_2_message(
            "user_1",
            companion["id"],
            InteractionUserMessageRequest(content="按我的背景回复。"),
        )

        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("personality: skeptical but fast-moving", prompt)
        self.assertIn("story: I am testing whether the product respects user background.", prompt)
        self.assertIn("name: Mira", prompt)

    def test_companion_2_enqueues_summary_and_memory_jobs_after_reply(self) -> None:
        derived_repository = FakeDerivedJobRepository()
        service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            derived_jobs=DerivedJobService(derived_repository),
        )
        companion = self.conversation_service.create_conversation(
            "user_1",
            ConversationCreateRequest(mode="companion_2"),
        )

        service.run_companion_2_message(
            "user_1",
            companion["id"],
            InteractionUserMessageRequest(content="我喜欢中文简短回复。"),
        )

        self.assertEqual([job["job_type"] for job in derived_repository.rows], ["summary", "memory_candidate"])
        self.assertEqual(derived_repository.rows[0]["source_message_ids"], ["message_1", "message_2"])

    def test_work_message_uses_task_state_and_enqueues_summary(self) -> None:
        derived_repository = FakeDerivedJobRepository()
        service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            derived_jobs=DerivedJobService(derived_repository),
        )
        work = self.conversation_service.create_conversation(
            "user_1",
            ConversationCreateRequest(mode="work"),
        )

        response = service.run_work_message(
            "user_1",
            work["id"],
            InteractionUserMessageRequest(content="下一步做什么？", targetAgentId="agent_2"),
            task_state={"objective": "Prepare a launch demo.", "status": "active"},
        )

        self.assertEqual(response["conversation"]["mode"], "work")
        self.assertEqual(response["agentMessage"]["senderSlot"], "agent_2")
        prompt = _prompt_text(self.model_runtime.requests[-1])
        self.assertIn("Current mode: work", prompt)
        self.assertIn("Prepare a launch demo.", prompt)
        self.assertEqual([job["job_type"] for job in derived_repository.rows], ["summary"])


def _prompt_text(request: ModelGenerateRequest) -> str:
    return "\n".join(message.content for message in request.messages)
