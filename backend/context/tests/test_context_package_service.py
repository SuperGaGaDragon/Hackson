"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import timedelta
from typing import Any
from unittest import TestCase

from context.builder import ContextBuilder
from context.schemas import AgentPersonaSnapshot, ContextBuildInput, ContextMode, ConversationMessage, SenderType
from context.service import ContextPackageService


class FakeContextPackageRepository:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes_ready = False

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"context_package_{len(self.rows) + 1}"
        self.rows.append(row)
        return row

    def list_prompt_logs(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return [row for row in self.rows if row["user_id"] == user_id and row.get("full_prompt_text")][:limit]

    def clear_prompt_text(self, user_id: str, timestamp) -> int:
        count = 0
        for row in self.rows:
            if row["user_id"] != user_id or not row.get("full_prompt_text"):
                continue
            row["full_prompt_text"] = None
            row["full_prompt_text_deleted_at"] = timestamp
            row["full_prompt_text_expires_at"] = None
            row["updated_at"] = timestamp
            count += 1
        return count

    def clear_expired_prompt_text(self, timestamp) -> int:
        count = 0
        for row in self.rows:
            expires_at = row.get("full_prompt_text_expires_at")
            if not row.get("full_prompt_text") or expires_at is None or expires_at > timestamp:
                continue
            row["full_prompt_text"] = None
            row["full_prompt_text_deleted_at"] = timestamp
            row["updated_at"] = timestamp
            count += 1
        return count


class ContextPackageServiceTest(TestCase):
    def setUp(self) -> None:
        self.repository = FakeContextPackageRepository()
        self.service = ContextPackageService(self.repository)
        self.package = ContextBuilder().build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_1",
                target_agent_id="agent_1",
                agents=[
                    AgentPersonaSnapshot(
                        id="agent_1",
                        name="Nora",
                        core_persona="A precise thinker.",
                    )
                ],
                recent_messages=[
                    ConversationMessage(
                        id="msg_1",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_2",
                        sender_name="Vale",
                        content="先讨论 demo 开场。",
                    )
                ],
                token_budget=6000,
            )
        )

    def test_persist_package_keeps_metadata_and_full_prompt_for_enabled_logging(self) -> None:
        record = self.service.persist_package(
            user_id="user_1",
            package=self.package,
            full_prompt_logging_enabled=True,
        )

        self.assertEqual(record["id"], "context_package_1")
        self.assertEqual(self.package.id, "context_package_1")
        self.assertEqual(record["conversationId"], "conv_1")
        self.assertEqual(record["targetAgentId"], "agent_1")
        self.assertEqual(record["includedMessageIds"], ["msg_1"])
        self.assertEqual(record["includedAgentIds"], ["agent_1"])
        self.assertEqual(record["promptHash"], self.package.prompt_hash)
        self.assertTrue(record["fullPromptLoggingEnabled"])
        self.assertTrue(record["fullPromptTextStored"])
        self.assertIn("Current mode: idle", record["fullPromptText"])
        retention = record["fullPromptTextExpiresAt"] - record["createdAt"]
        self.assertEqual(retention, timedelta(days=30))

    def test_persist_package_omits_full_prompt_when_logging_disabled(self) -> None:
        record = self.service.persist_package(
            user_id="user_1",
            package=self.package,
            full_prompt_logging_enabled=False,
        )

        self.assertEqual(record["id"], "context_package_1")
        self.assertFalse(record["fullPromptLoggingEnabled"])
        self.assertFalse(record["fullPromptTextStored"])
        self.assertIsNone(record["fullPromptText"])
        self.assertIsNone(record["fullPromptTextExpiresAt"])
        self.assertEqual(record["includedMessageIds"], ["msg_1"])
        self.assertEqual(record["promptHash"], self.package.prompt_hash)

    def test_delete_prompt_logs_clears_text_but_leaves_package_metadata(self) -> None:
        first = self.service.persist_package(
            user_id="user_1",
            package=self.package,
            full_prompt_logging_enabled=True,
        )
        self.service.persist_package(
            user_id="user_1",
            package=self.package,
            full_prompt_logging_enabled=False,
        )

        response = self.service.delete_prompt_logs("user_1")

        self.assertEqual(response["deletedPromptLogs"], 1)
        self.assertEqual(len(self.repository.rows), 2)
        self.assertIsNone(self.repository.rows[0]["full_prompt_text"])
        self.assertEqual(self.repository.rows[0]["prompt_hash"], first["promptHash"])
        self.assertEqual(self.repository.rows[0]["included_message_ids"], ["msg_1"])

    def test_expired_prompt_text_is_cleared_without_deleting_metadata(self) -> None:
        first = self.service.persist_package(
            user_id="user_1",
            package=self.package,
            full_prompt_logging_enabled=True,
        )
        self.repository.rows[0]["full_prompt_text_expires_at"] = first["createdAt"] - timedelta(seconds=1)

        logs = self.service.list_prompt_logs("user_1")

        self.assertEqual(logs["promptLogs"], [])
        self.assertEqual(len(self.repository.rows), 1)
        self.assertIsNone(self.repository.rows[0]["full_prompt_text"])
        self.assertEqual(self.repository.rows[0]["prompt_hash"], first["promptHash"])
