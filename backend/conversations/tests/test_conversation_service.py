"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService


class FakeConversationRepository:
    def __init__(self) -> None:
        self.conversations: dict[str, dict[str, Any]] = {}
        self.messages: dict[str, list[dict[str, Any]]] = {}
        self.indexes_ready = False
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create_conversation(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["_id"] = str(self.next_id)
        self.next_id += 1
        self.conversations[document["_id"]] = document
        self.messages[document["_id"]] = []
        return document

    def find_conversation(self, conversation_id: str, user_id: str) -> dict[str, Any] | None:
        document = self.conversations.get(conversation_id)
        if document is None or document["user_id"] != user_id:
            return None
        return document

    def list_conversations(
        self,
        user_id: str,
        mode: str | None,
        status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        rows = [
            document
            for document in self.conversations.values()
            if document["user_id"] == user_id
            and (mode is None or document["mode"] == mode)
            and (status is None or document["status"] == status)
        ]
        return rows[:limit]

    def find_active_idle_conversation(self, user_id: str) -> dict[str, Any] | None:
        return next(
            (
                document
                for document in self.conversations.values()
                if document["user_id"] == user_id
                and document["mode"] == "idle"
                and document["status"] == "active"
            ),
            None,
        )

    def append_message(self, conversation: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]:
        conversation_id = conversation["_id"]
        message = dict(message)
        message["_id"] = f"message_{len(self.messages[conversation_id]) + 1}"
        message["sequence"] = len(self.messages[conversation_id]) + 1
        self.messages[conversation_id].append(message)
        conversation["message_count"] += 1
        conversation["last_message_at"] = message["created_at"]
        conversation["updated_at"] = message["created_at"]
        return message

    def list_messages(
        self,
        conversation_id: str,
        user_id: str,
        after_sequence: int | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        rows = [
            message
            for message in self.messages.get(conversation_id, [])
            if message["user_id"] == user_id
            and (after_sequence is None or message["sequence"] > after_sequence)
        ]
        return rows[:limit]


class ConversationServiceTest(TestCase):
    def test_get_or_create_active_idle_reuses_existing_conversation(self) -> None:
        service = ConversationService(FakeConversationRepository())
        first = service.get_or_create_active_idle("user_1")
        second = service.get_or_create_active_idle("user_1")

        self.assertEqual(first["id"], second["id"])
        self.assertEqual(first["mode"], "idle")
        self.assertEqual(first["participantSlots"], ["agent_1", "agent_2"])

    def test_append_agent_message_requires_agent_slot(self) -> None:
        service = ConversationService(FakeConversationRepository())
        conversation = service.create_conversation("user_1", ConversationCreateRequest(mode="companion_2"))

        with self.assertRaises(Exception):
            service.append_message(
                "user_1",
                conversation["id"],
                MessageAppendRequest(
                    sender_type="agent",
                    role="assistant",
                    content="missing slot",
                ),
            )

    def test_append_and_page_messages_by_sequence(self) -> None:
        service = ConversationService(FakeConversationRepository())
        conversation = service.create_conversation("user_1", ConversationCreateRequest(mode="companion_2"))
        service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(sender_type="user", sender_id="user_1", role="user", content="hello"),
        )
        service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="hi",
            ),
        )

        page = service.list_messages("user_1", conversation["id"], after_sequence=0, limit=10)

        self.assertEqual([message["sequence"] for message in page["messages"]], [1, 2])
        self.assertIsNone(page["nextAfterSequence"])
