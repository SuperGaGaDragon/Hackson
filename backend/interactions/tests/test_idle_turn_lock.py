"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

import mongomock
from fastapi import HTTPException

from conversations.schemas import MessageAppendRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from context.builder import ContextBuilder
from interactions.locks import IdleTurnLockRepository, IdleTurnLockService, now_utc
from interactions.schemas import IdleTickRequest, IdleUserMessageRequest
from interactions.service import InteractionService
from interactions.tests.test_interaction_service import FailingModelRuntime, FakeModelRuntime
from model_runtime.errors import ModelRuntimeError


class FakeIdleTurnLockRepository:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str, int], dict[str, Any]] = {}
        self.idempotency: dict[tuple[str, str], tuple[str, str, int]] = {}
        self.indexes_ready = False

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def acquire(self, document: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        transcript_key = (document["user_id"], document["conversation_id"], document["message_count"])
        idempotency_key = (document["user_id"], document["idempotency_key"])
        if idempotency_key in self.idempotency:
            row = self.rows[self.idempotency[idempotency_key]]
            return False, row
        existing = self.rows.get(transcript_key)
        if existing and existing["status"] == "running":
            return False, existing
        row = dict(document)
        row["_id"] = f"idle_turn_lock_{len(self.rows) + 1}"
        self.rows[transcript_key] = row
        self.idempotency[idempotency_key] = transcript_key
        return True, row

    def complete(self, lock_id: str, response: dict[str, Any], timestamp) -> dict[str, Any]:
        row = self._row(lock_id)
        row["status"] = "completed"
        row["response"] = response
        row["updated_at"] = timestamp
        return row

    def fail(self, lock_id: str, error_detail: str, timestamp) -> dict[str, Any]:
        row = self._row(lock_id)
        row["status"] = "failed"
        row["error_detail"] = error_detail
        row["updated_at"] = timestamp
        return row

    def _row(self, lock_id: str) -> dict[str, Any]:
        return next(row for row in self.rows.values() if row["_id"] == lock_id)


class IdleTurnLockTest(TestCase):
    def setUp(self) -> None:
        self.conversation_service = ConversationService(FakeConversationRepository())
        self.model_runtime = FakeModelRuntime()
        self.lock_repository = FakeIdleTurnLockRepository()
        self.service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=self.model_runtime,
            idle_turn_locks=IdleTurnLockService(self.lock_repository),
        )

    def test_same_idempotency_key_returns_completed_idle_tick_response(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")

        first = self.service.run_idle_tick(
            "user_1",
            idle["id"],
            IdleTickRequest(idempotencyKey="tick-1"),
        )
        second = self.service.run_idle_tick(
            "user_1",
            idle["id"],
            IdleTickRequest(idempotencyKey="tick-1"),
        )

        self.assertEqual(first["agentMessage"]["id"], second["agentMessage"]["id"])
        self.assertEqual(first["context"]["promptHash"], second["context"]["promptHash"])
        self.assertEqual(len(self.model_runtime.requests), 1)

    def test_different_key_for_running_same_transcript_returns_idle_turn_locked(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        self.lock_repository.acquire(
            {
                "user_id": "user_1",
                "conversation_id": idle["id"],
                "message_count": idle["messageCount"],
                "idempotency_key": "first",
                "status": "running",
            }
        )

        with self.assertRaises(HTTPException) as error:
            self.service.run_idle_tick(
                "user_1",
                idle["id"],
                IdleTickRequest(idempotencyKey="second"),
            )

        self.assertEqual(error.exception.status_code, 423)
        self.assertEqual(error.exception.detail, "idle_turn_locked")
        self.assertEqual(len(self.model_runtime.requests), 0)

    def test_failed_idle_tick_marks_lock_failed_and_later_tick_can_run(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        failing_service = InteractionService(
            conversation_service=self.conversation_service,
            context_builder=ContextBuilder(),
            model_runtime=FailingModelRuntime(ModelRuntimeError("model_network_error")),
            idle_turn_locks=IdleTurnLockService(self.lock_repository),
        )

        with self.assertRaises(HTTPException):
            failing_service.run_idle_tick(
                "user_1",
                idle["id"],
                IdleTickRequest(idempotencyKey="will-fail"),
            )

        success = self.service.run_idle_tick(
            "user_1",
            idle["id"],
            IdleTickRequest(idempotencyKey="after-fail"),
        )

        self.assertEqual(success["agentMessage"]["sequence"], 1)
        self.assertEqual(len(self.model_runtime.requests), 1)

    def test_message_count_is_part_of_lock_key(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        self.service.run_idle_tick("user_1", idle["id"], IdleTickRequest(idempotencyKey="first-count"))
        self.conversation_service.append_message(
            "user_1",
            idle["id"],
            MessageAppendRequest(sender_type="user", sender_id="user_1", role="user", content="继续"),
        )

        response = self.service.run_idle_tick("user_1", idle["id"], IdleTickRequest(idempotencyKey="second-count"))

        self.assertEqual(response["agentMessage"]["sequence"], 3)
        self.assertEqual(len(self.model_runtime.requests), 2)

    def test_same_idempotency_key_returns_completed_idle_say_response(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")

        first = self.service.run_idle_user_message(
            "user_1",
            idle["id"],
            IdleUserMessageRequest(content="我插一句。", idempotencyKey="say-1"),
        )
        second = self.service.run_idle_user_message(
            "user_1",
            idle["id"],
            IdleUserMessageRequest(content="我插一句。", idempotencyKey="say-1"),
        )

        self.assertEqual(first["userMessage"]["id"], second["userMessage"]["id"])
        self.assertEqual(first["agentMessage"]["id"], second["agentMessage"]["id"])
        self.assertEqual(len(self.model_runtime.requests), 1)

    def test_idle_say_returns_locked_when_tick_is_running_for_same_transcript(self) -> None:
        idle = self.conversation_service.get_or_create_active_idle("user_1")
        self.lock_repository.acquire(
            {
                "user_id": "user_1",
                "conversation_id": idle["id"],
                "message_count": idle["messageCount"],
                "idempotency_key": "tick-running",
                "status": "running",
            }
        )

        with self.assertRaises(HTTPException) as error:
            self.service.run_idle_user_message(
                "user_1",
                idle["id"],
                IdleUserMessageRequest(content="我现在插一句。", idempotencyKey="say-while-running"),
            )

        self.assertEqual(error.exception.status_code, 423)
        self.assertEqual(error.exception.detail, "idle_turn_locked")
        self.assertEqual(len(self.model_runtime.requests), 0)


class IdleTurnLockRepositoryTest(TestCase):
    def test_mongo_repository_completes_object_id_lock(self) -> None:
        repository = IdleTurnLockRepository(mongomock.MongoClient()["idle_lock_test"])
        service = IdleTurnLockService(repository)

        acquired, lock = service.acquire(
            user_id="user_1",
            conversation_id="conv_1",
            message_count=0,
            idempotency_key="tick-1",
        )
        self.assertTrue(acquired)

        completed = service.complete(lock["_id"], {"ok": True})

        self.assertEqual(completed["status"], "completed")
        self.assertEqual(completed["response"], {"ok": True})

    def test_mongo_repository_failed_transcript_can_be_retried(self) -> None:
        repository = IdleTurnLockRepository(mongomock.MongoClient()["idle_lock_retry_test"])
        service = IdleTurnLockService(repository)
        acquired, lock = service.acquire(
            user_id="user_1",
            conversation_id="conv_1",
            message_count=0,
            idempotency_key="tick-fails",
        )
        self.assertTrue(acquired)
        service.fail(lock["_id"], "model_unavailable")

        retry_acquired, retry_lock = service.acquire(
            user_id="user_1",
            conversation_id="conv_1",
            message_count=0,
            idempotency_key="tick-retry",
        )

        self.assertTrue(retry_acquired)
        self.assertEqual(retry_lock["status"], "running")
