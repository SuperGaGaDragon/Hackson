"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase
from unittest.mock import Mock

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from diary.service import DiaryService
from diary.tests.test_diary_service import FakeDiaryRepository
from memory.service import MemoryService
from memory.tests.test_memory_service import FakeMemoryRepository
from summaries.service import SummaryService
from summaries.tests.test_summary_service import FakeSummaryRepository
from workers.derived_jobs import DerivedJobCreateRequest, DerivedJobService
from workers.diary_worker import DiaryWorker
from workers.memory_worker import MemoryWorker
from workers.relationship_worker import RelationshipWorker
from workers.runner import DerivedWorkerRunner
from workers.runner import DerivedWorkerLoop
from workers.summary_worker import SummaryWorker
from workers.tests.test_derived_jobs import FakeDerivedJobRepository


class DerivedWorkerRunnerTest(TestCase):
    def test_runner_processes_summary_memory_diary_and_relationship_jobs(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        job_repository = FakeDerivedJobRepository()
        summary_repository = FakeSummaryRepository()
        memory_repository = FakeMemoryRepository()
        diary_repository = FakeDiaryRepository()
        job_service = DerivedJobService(job_repository)
        conversation = conversation_service.create_conversation("user_1", ConversationCreateRequest(mode="idle"))
        user_message = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id="user_1",
                role="user",
                content="我喜欢中文简短回复。",
            ),
        )
        first_agent_message = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="那我保持简短。",
            ),
        )
        second_agent_message = conversation_service.append_message(
            "user_1",
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="我会接住这个偏好，之后少绕圈。",
            ),
        )
        source_ids = [user_message["id"], first_agent_message["id"], second_agent_message["id"]]
        for job_type in ["summary", "memory_candidate", "diary", "relationship"]:
            job_service.enqueue(
                DerivedJobCreateRequest(
                    job_type=job_type,
                    user_id="user_1",
                    conversation_id=conversation["id"],
                    source_message_ids=source_ids,
                    metadata={"target_agent_id": "agent_1", "summary_type": "session"},
                )
            )
        runner = DerivedWorkerRunner(
            job_service,
            SummaryWorker(conversation_service, SummaryService(summary_repository)),
            MemoryWorker(conversation_service, MemoryService(memory_repository)),
            DiaryWorker(DiaryService(diary_repository)),
            RelationshipWorker(conversation_service, MemoryService(memory_repository)),
        )

        processed = runner.run_once(limit=10)

        self.assertEqual(processed, 4)
        self.assertEqual([row["status"] for row in job_repository.rows], ["succeeded"] * 4)
        self.assertEqual(len(summary_repository.rows), 1)
        self.assertIn("我喜欢中文简短回复", summary_repository.rows[0]["content"])
        self.assertEqual(len(diary_repository.rows), 1)
        self.assertEqual(diary_repository.rows[0]["source_message_ids"], source_ids)
        self.assertTrue(any(row["memory_type"] == "preference" for row in memory_repository.rows))
        self.assertTrue(any(row["memory_type"] == "relationship" for row in memory_repository.rows))

    def test_background_loop_runs_fifo_and_freshness_lane(self) -> None:
        runner = Mock()
        stop_after_first_wait = Mock()
        stop_after_first_wait.is_set.side_effect = [False, True]
        loop = DerivedWorkerLoop(runner=runner, interval_seconds=0.2, batch_size=8, _stop_event=stop_after_first_wait)

        loop._run()

        self.assertEqual(runner.run_once.call_args_list[0].kwargs, {"limit": 8})
        self.assertEqual(runner.run_once.call_args_list[1].kwargs, {"limit": 2, "newest_first": True})
        stop_after_first_wait.wait.assert_called_once_with(0.2)
