"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from summaries.schemas import SummaryCreateRequest
from summaries.service import SummaryService


class FakeSummaryRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.rows: list[dict[str, Any]] = []
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create_summary(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"summary_{self.next_id}"
        self.next_id += 1
        self.rows.append(row)
        return row

    def get_latest_summary(
        self,
        user_id: str,
        conversation_id: str,
        summary_type: str,
    ) -> dict[str, Any] | None:
        matches = [
            row
            for row in self.rows
            if row["user_id"] == user_id
            and row["conversation_id"] == conversation_id
            and row["summary_type"] == summary_type
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda row: row["updated_at"], reverse=True)[0]


class SummaryServiceTest(TestCase):
    def test_create_summary_requires_source_message_range(self) -> None:
        service = SummaryService(FakeSummaryRepository())

        with self.assertRaises(Exception):
            service.create_summary(
                "user_1",
                SummaryCreateRequest(
                    conversation_id="conversation_1",
                    summary_type="session",
                    content="User and Nora discussed the demo.",
                    source_message_start_id="message_1",
                    source_message_end_id=None,
                ),
            )

    def test_latest_summary_returns_context_snapshot_shape(self) -> None:
        repository = FakeSummaryRepository()
        service = SummaryService(repository)

        created = service.create_summary(
            "user_1",
            SummaryCreateRequest(
                conversation_id="conversation_1",
                summary_type="session",
                content="User prefers practical demo planning.",
                source_message_start_id="message_1",
                source_message_end_id="message_8",
            ),
        )
        latest = service.get_latest_summary("user_1", "conversation_1", "session")

        self.assertTrue(repository.indexes_ready)
        self.assertEqual(created["sourceMessageStartId"], "message_1")
        self.assertEqual(latest.id, created["id"])
        self.assertEqual(latest.summary_type, "session")
        self.assertIn("practical demo", latest.content)
