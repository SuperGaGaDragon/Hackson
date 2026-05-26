"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from diary.schemas import DiaryEntryCreateRequest
from diary.service import DiaryService


class FakeDiaryRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.rows: list[dict[str, Any]] = []
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create_diary_entry(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"diary_{self.next_id}"
        self.next_id += 1
        self.rows.append(row)
        return row

    def list_diary_entries(self, user_id: str, agent_id: str | None, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.rows
            if row["user_id"] == user_id and (agent_id is None or row["agent_id"] == agent_id)
        ][:limit]


class DiaryServiceTest(TestCase):
    def test_rejects_diary_without_evidence(self) -> None:
        service = DiaryService(FakeDiaryRepository())

        with self.assertRaises(Exception):
            service.create_entry(
                "user_1",
                DiaryEntryCreateRequest(
                    agent_id="agent_1",
                    content="Today felt meaningful.",
                    source_message_ids=[],
                ),
            )

    def test_creates_evidence_backed_diary_entry(self) -> None:
        repository = FakeDiaryRepository()
        service = DiaryService(repository)

        entry = service.create_entry(
            "user_1",
            DiaryEntryCreateRequest(
                agent_id="agent_1",
                content="Nora reflected on the idle conversation.",
                source_message_ids=["message_1", "message_2"],
            ),
        )

        self.assertTrue(repository.indexes_ready)
        self.assertEqual(entry["agentId"], "agent_1")
        self.assertEqual(entry["sourceMessageIds"], ["message_1", "message_2"])
