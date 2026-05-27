"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from conversations.schemas import ConversationCreateRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from context.builder import ContextBuilder
from interactions.routes import companion_router, get_interaction_service, idle_router
from interactions.service import InteractionService
from interactions.tests.test_interaction_service import FakeModelRuntime
from users.auth import get_current_user_id


TEST_USER_ID = "route_user"


class InteractionRoutesTest(TestCase):
    def setUp(self) -> None:
        self.conversation_service = ConversationService(FakeConversationRepository())
        self.model_runtime = FakeModelRuntime()
        self.service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
        )
        app = FastAPI()
        app.include_router(idle_router, prefix="/api/idle")
        app.include_router(companion_router, prefix="/api/companion")
        app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
        app.dependency_overrides[get_interaction_service] = lambda: self.service
        self.client = TestClient(app)

    def test_idle_tick_route_generates_agent_message(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle(TEST_USER_ID)

        response = self.client.post(
            f"/api/idle/{idle['id']}/tick",
            json={
                "targetAgentId": "agent_2",
                "idleSeed": "继续聊 V1 demo 的目标。",
                "metadata": {"source": "route_test"},
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["conversation"]["mode"], "idle")
        self.assertEqual(body["conversation"]["messageCount"], 1)
        self.assertIsNone(body["userMessage"])
        self.assertEqual(body["agentMessage"]["senderType"], "agent")
        self.assertEqual(body["agentMessage"]["senderSlot"], "agent_2")
        self.assertEqual(body["context"]["modelName"], "fake-model")
        self.assertIn("promptHash", body["context"])

    def test_idle_tick_route_accepts_discussion_direction_without_saving_user_message(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle(TEST_USER_ID)

        response = self.client.post(
            f"/api/idle/{idle['id']}/tick",
            json={
                "targetAgentId": "agent_2",
                "discussionDirection": "从用户控制话题方向展开",
            },
        )

        self.assertEqual(response.status_code, 201)
        prompt = "\n".join(message.content for message in self.model_runtime.requests[-1].messages)
        self.assertIn("User direction:", prompt)
        self.assertIn("从用户控制话题方向展开", prompt)
        messages = self.conversation_service.list_messages(
            TEST_USER_ID,
            idle["id"],
            after_sequence=0,
            created_after=None,
            created_before=None,
            limit=10,
        )
        self.assertEqual([message["senderType"] for message in messages["messages"]], ["agent"])

    def test_idle_join_route_creates_companion_1_child(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle(TEST_USER_ID)

        response = self.client.post(
            f"/api/idle/{idle['id']}/join",
            json={
                "content": "我现在加入这个 idle 话题。",
                "targetAgentId": "agent_1",
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["conversation"]["mode"], "companion_1")
        self.assertEqual(body["conversation"]["parentConversationId"], idle["id"])
        self.assertEqual(body["conversation"]["messageCount"], 2)
        self.assertEqual(body["userMessage"]["content"], "我现在加入这个 idle 话题。")
        self.assertEqual(body["agentMessage"]["sequence"], 2)
        self.assertIn("promptHash", body["context"])

    def test_companion_route_continues_companion_1_child(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle(TEST_USER_ID)
        joined = self.client.post(
            f"/api/idle/{idle['id']}/join",
            json={
                "content": "我现在加入这个 idle 话题。",
                "targetAgentId": "agent_1",
            },
        ).json()

        response = self.client.post(
            f"/api/companion/{joined['conversation']['id']}/messages",
            json={
                "content": "继续说。",
                "targetAgentId": "agent_2",
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["conversation"]["mode"], "companion_1")
        self.assertEqual(body["conversation"]["parentConversationId"], idle["id"])
        self.assertEqual(body["conversation"]["messageCount"], 4)
        self.assertEqual(body["userMessage"]["sequence"], 3)
        self.assertEqual(body["agentMessage"]["sequence"], 4)
        self.assertEqual(body["agentMessage"]["senderSlot"], "agent_2")

    def test_companion_message_route_saves_user_and_agent_messages(self) -> None:
        companion = self.conversation_service.create_conversation(
            TEST_USER_ID,
            ConversationCreateRequest(mode="companion_2", title="Route test"),
        )

        response = self.client.post(
            f"/api/companion/{companion['id']}/messages",
            json={
                "content": "一句话说明 API 主链路。",
                "targetAgentId": "agent_2",
            },
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["conversation"]["mode"], "companion_2")
        self.assertEqual(body["conversation"]["messageCount"], 2)
        self.assertEqual(body["userMessage"]["sequence"], 1)
        self.assertEqual(body["agentMessage"]["sequence"], 2)
        self.assertEqual(body["agentMessage"]["senderSlot"], "agent_2")
        messages = self.conversation_service.list_messages(
            TEST_USER_ID,
            companion["id"],
            after_sequence=0,
            created_after=None,
            created_before=None,
            limit=10,
        )
        self.assertEqual([message["sequence"] for message in messages["messages"]], [1, 2])
