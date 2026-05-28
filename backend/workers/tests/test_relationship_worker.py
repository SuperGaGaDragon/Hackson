"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from memory.service import MemoryService
from memory.tests.test_memory_service import FakeMemoryRepository
from workers.derived_jobs import DerivedJobCreateRequest, DerivedJobService
from workers.relationship_worker import RelationshipWorker
from workers.tests.test_derived_jobs import FakeDerivedJobRepository


class RelationshipWorkerTest(TestCase):
    def test_rejects_single_agent_turn_without_relationship_evidence(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        memory_repository = FakeMemoryRepository()
        worker = RelationshipWorker(conversation_service, MemoryService(memory_repository))
        job_service = DerivedJobService(FakeDerivedJobRepository())
        conversation = conversation_service.create_conversation("user_1", ConversationCreateRequest(mode="idle"))
        message = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="今天继续聊意义。",
            ),
        )
        job_service.enqueue(
            DerivedJobCreateRequest(
                job_type="relationship",
                user_id="user_1",
                conversation_id=conversation["id"],
                source_message_ids=[message["id"]],
            )
        )

        job_service.run_pending({"relationship": worker.handle})

        self.assertEqual(memory_repository.rows, [])

    def test_creates_content_derived_relationship_memory(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        memory_repository = FakeMemoryRepository()
        worker = RelationshipWorker(conversation_service, MemoryService(memory_repository))
        job_service = DerivedJobService(FakeDerivedJobRepository())
        conversation = conversation_service.create_conversation("user_1", ConversationCreateRequest(mode="idle"))
        first = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="别急着找人生意义，先看今天哪一刻没有白过。",
            ),
        )
        second = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="我同意，但更想问哪种辛苦你承受之后还觉得值。",
            ),
        )
        job_service.enqueue(
            DerivedJobCreateRequest(
                job_type="relationship",
                user_id="user_1",
                conversation_id=conversation["id"],
                source_message_ids=[first["id"], second["id"]],
            )
        )

        job_service.run_pending({"relationship": worker.handle})

        self.assertEqual(len(memory_repository.rows), 1)
        row = memory_repository.rows[0]
        self.assertEqual(row["memory_type"], "relationship")
        self.assertNotEqual(row["summary"], "Nora and Vale shared another idle interaction.")
        self.assertIn("Nora", row["summary"])
        self.assertIn("Vale", row["summary"])
        self.assertIn("意义", row["summary"])
