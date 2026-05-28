"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from workers.derived_jobs import DerivedJobCreateRequest, DerivedJobService


class FakeDerivedJobRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.rows: list[dict[str, Any]] = []
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create_job(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"job_{self.next_id}"
        self.next_id += 1
        self.rows.append(row)
        return row

    def find_pending_jobs(
        self,
        limit: int,
        user_id: str | None = None,
        conversation_id: str | None = None,
        newest_first: bool = False,
    ) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self.rows
            if row["status"] == "pending"
            and (user_id is None or row["user_id"] == user_id)
            and (conversation_id is None or row["conversation_id"] == conversation_id)
        ]
        if newest_first:
            rows = list(reversed(rows))
        return rows[:limit]

    def mark_job_running(self, job_id: str) -> dict[str, Any] | None:
        return self._update(job_id, {"status": "running"})

    def mark_job_succeeded(self, job_id: str) -> dict[str, Any] | None:
        return self._update(job_id, {"status": "succeeded"})

    def mark_job_failed(self, job_id: str, error: str) -> dict[str, Any] | None:
        return self._update(job_id, {"status": "failed", "last_error": error})

    def _update(self, job_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        for row in self.rows:
            if row["_id"] == job_id:
                row.update(values)
                row["attempt_count"] += 1 if values.get("status") == "running" else 0
                return row
        return None


class DerivedJobServiceTest(TestCase):
    def test_enqueue_requires_source_messages(self) -> None:
        service = DerivedJobService(FakeDerivedJobRepository())

        with self.assertRaises(Exception):
            service.enqueue(
                DerivedJobCreateRequest(
                    job_type="memory_candidate",
                    user_id="user_1",
                    conversation_id="conversation_1",
                    source_message_ids=[],
                )
            )

    def test_run_pending_marks_failure_without_raising(self) -> None:
        repository = FakeDerivedJobRepository()
        service = DerivedJobService(repository)
        service.enqueue(
            DerivedJobCreateRequest(
                job_type="memory_candidate",
                user_id="user_1",
                conversation_id="conversation_1",
                source_message_ids=["message_1"],
            )
        )

        processed = service.run_pending({"memory_candidate": lambda job: (_ for _ in ()).throw(RuntimeError("boom"))})

        self.assertTrue(repository.indexes_ready)
        self.assertEqual(processed, 1)
        self.assertEqual(repository.rows[0]["status"], "failed")
        self.assertEqual(repository.rows[0]["last_error"], "boom")

    def test_run_pending_executes_registered_handler_and_marks_success(self) -> None:
        repository = FakeDerivedJobRepository()
        service = DerivedJobService(repository)
        seen: list[str] = []
        service.enqueue(
            DerivedJobCreateRequest(
                job_type="summary",
                user_id="user_1",
                conversation_id="conversation_1",
                source_message_ids=["message_1"],
            )
        )

        processed = service.run_pending({"summary": lambda job: seen.append(job.id)})

        self.assertEqual(processed, 1)
        self.assertEqual(seen, ["job_1"])
        self.assertEqual(repository.rows[0]["status"], "succeeded")

    def test_run_pending_can_scope_to_user_and_conversation(self) -> None:
        repository = FakeDerivedJobRepository()
        service = DerivedJobService(repository)
        service.enqueue(
            DerivedJobCreateRequest(
                job_type="summary",
                user_id="old_user",
                conversation_id="old_conversation",
                source_message_ids=["message_1"],
            )
        )
        service.enqueue(
            DerivedJobCreateRequest(
                job_type="summary",
                user_id="current_user",
                conversation_id="current_conversation",
                source_message_ids=["message_2"],
            )
        )
        seen: list[str] = []

        processed = service.run_pending(
            {"summary": lambda job: seen.append(job.id)},
            user_id="current_user",
            conversation_id="current_conversation",
        )

        self.assertEqual(processed, 1)
        self.assertEqual(seen, ["job_2"])
        self.assertEqual(repository.rows[0]["status"], "pending")
        self.assertEqual(repository.rows[1]["status"], "succeeded")

    def test_run_pending_skips_job_when_claim_loses_race(self) -> None:
        class RacingRepository(FakeDerivedJobRepository):
            def mark_job_running(self, job_id: str) -> dict[str, Any] | None:
                return None

        repository = RacingRepository()
        service = DerivedJobService(repository)
        service.enqueue(
            DerivedJobCreateRequest(
                job_type="summary",
                user_id="user_1",
                conversation_id="conversation_1",
                source_message_ids=["message_1"],
            )
        )
        seen: list[str] = []

        processed = service.run_pending({"summary": lambda job: seen.append(job.id)})

        self.assertEqual(processed, 0)
        self.assertEqual(seen, [])
        self.assertEqual(repository.rows[0]["status"], "pending")

    def test_run_pending_can_process_newest_pending_first(self) -> None:
        repository = FakeDerivedJobRepository()
        service = DerivedJobService(repository)
        for index in range(3):
            service.enqueue(
                DerivedJobCreateRequest(
                    job_type="summary",
                    user_id=f"user_{index}",
                    conversation_id=f"conversation_{index}",
                    source_message_ids=[f"message_{index}"],
                )
            )
        seen: list[str] = []

        processed = service.run_pending(
            {"summary": lambda job: seen.append(job.id)},
            limit=1,
            newest_first=True,
        )

        self.assertEqual(processed, 1)
        self.assertEqual(seen, ["job_3"])
        self.assertEqual(repository.rows[0]["status"], "pending")
        self.assertEqual(repository.rows[2]["status"], "succeeded")
