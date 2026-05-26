"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from unittest import TestCase

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from memory.service import MemoryService
from memory.tests.test_memory_service import FakeMemoryRepository
from workers.derived_jobs import DerivedJobCreateRequest, DerivedJobService
from workers.memory_worker import MemoryWorker
from workers.tests.test_derived_jobs import FakeDerivedJobRepository


class MemoryWorkerTest(TestCase):
    def test_user_explicit_preference_becomes_memory_card(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        memory_repository = FakeMemoryRepository()
        worker = MemoryWorker(conversation_service, MemoryService(memory_repository))
        job_service = DerivedJobService(FakeDerivedJobRepository())
        conversation = conversation_service.create_conversation("user_1", ConversationCreateRequest(mode="companion_2"))
        message = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id="user_1",
                role="user",
                content="我喜欢中文简短回复。",
            ),
        )
        job = job_service.enqueue(
            DerivedJobCreateRequest(
                job_type="memory_candidate",
                user_id="user_1",
                conversation_id=conversation["id"],
                source_message_ids=[message["id"]],
            )
        )

        job_service.run_pending({"memory_candidate": worker.handle})

        cards = MemoryService(memory_repository).list_context_memory(
            "user_1",
            scope="companion",
            owner_type="user",
            owner_id="user_1",
        )
        self.assertEqual(len(cards), 1)
        self.assertIn("我喜欢中文简短回复", cards[0].summary)
