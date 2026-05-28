"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from memory.schemas import MemoryCandidate
from memory.service import MemoryService


class FakeMemoryRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.rows: list[dict[str, Any]] = []
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def upsert_memory_card(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"memory_{self.next_id}"
        self.next_id += 1
        self.rows.append(row)
        return row

    def list_memory_cards(
        self,
        user_id: str,
        scope: str,
        owner_type: str | None,
        owner_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self.rows
            if row["user_id"] == user_id
            and row["scope"] == scope
            and row["status"] == "active"
            and (owner_type is None or row["owner_type"] == owner_type)
            and (owner_id is None or row["owner_id"] == owner_id)
        ]
        rows = sorted(rows, key=lambda row: (row["importance_score"], row["updated_at"]), reverse=True)
        return rows[:limit]

    def list_user_memory_cards(self, user_id: str, include_deleted: bool, limit: int) -> list[dict[str, Any]]:
        rows = [row for row in self.rows if row["user_id"] == user_id]
        if not include_deleted:
            rows = [row for row in rows if row["status"] != "deleted"]
        rows = sorted(rows, key=lambda row: (row["updated_at"], row["importance_score"]), reverse=True)
        return rows[:limit]

    def find_memory_card(self, user_id: str, memory_id: str) -> dict[str, Any] | None:
        for row in self.rows:
            if row["user_id"] == user_id and row["_id"] == memory_id:
                return row
        return None

    def update_memory_status(self, user_id: str, memory_id: str, status: str, timestamp) -> dict[str, Any] | None:
        row = self.find_memory_card(user_id, memory_id)
        if row is None:
            return None
        row["status"] = status
        row["updated_at"] = timestamp
        return row


class MemoryServiceTest(TestCase):
    def test_rejects_memory_without_source_message_ids(self) -> None:
        service = MemoryService(FakeMemoryRepository())

        accepted = service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="companion",
                owner_type="user",
                owner_id="user_1",
                memory_type="preference",
                summary="User prefers Chinese.",
                source_message_ids=[],
                source_sender_types=["user"],
                importance_score=0.8,
                confidence=0.9,
            ),
        )

        self.assertIsNone(accepted)

    def test_rejects_user_fact_from_agent_only_evidence(self) -> None:
        service = MemoryService(FakeMemoryRepository())

        accepted = service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="companion",
                owner_type="user",
                owner_id="user_1",
                memory_type="fact",
                summary="User lives in Toronto.",
                source_message_ids=["message_1"],
                source_sender_types=["agent"],
                importance_score=0.8,
                confidence=0.9,
            ),
        )

        self.assertIsNone(accepted)

    def test_lists_only_active_memory_for_requested_user_and_scope(self) -> None:
        repository = FakeMemoryRepository()
        service = MemoryService(repository)
        service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="companion",
                owner_type="user",
                owner_id="user_1",
                memory_type="preference",
                summary="User prefers concise Chinese replies.",
                source_message_ids=["message_1"],
                source_sender_types=["user"],
                importance_score=0.8,
                confidence=0.9,
            ),
        )
        service.accept_candidate(
            "user_2",
            MemoryCandidate(
                scope="companion",
                owner_type="user",
                owner_id="user_2",
                memory_type="preference",
                summary="Other user prefers English.",
                source_message_ids=["message_2"],
                source_sender_types=["user"],
                importance_score=1.0,
                confidence=0.9,
            ),
        )
        service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="work",
                owner_type="task",
                owner_id="task_1",
                memory_type="task",
                summary="Work task must stay isolated.",
                source_message_ids=["message_3"],
                source_sender_types=["user"],
                importance_score=1.0,
                confidence=0.9,
            ),
        )

        cards = service.list_context_memory("user_1", scope="companion", owner_type="user", owner_id="user_1")

        self.assertTrue(repository.indexes_ready)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].summary, "User prefers concise Chinese replies.")

    def test_user_can_disable_and_delete_memory_without_context_reads(self) -> None:
        repository = FakeMemoryRepository()
        service = MemoryService(repository)
        created = service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="companion",
                owner_type="user",
                owner_id="user_1",
                memory_type="preference",
                summary="User prefers direct replies.",
                source_message_ids=["message_1"],
                source_sender_types=["user"],
                importance_score=0.8,
                confidence=0.9,
            ),
        )
        assert created is not None

        disabled = service.update_status("user_1", created["id"], "disabled")

        self.assertEqual(disabled["status"], "disabled")
        self.assertEqual(service.list_context_memory("user_1", "companion"), [])
        self.assertEqual(len(service.list_user_memory("user_1")["memoryCards"]), 1)

        deleted = service.delete_memory("user_1", created["id"])

        self.assertEqual(deleted, {"deletedMemoryCard": True})
        self.assertEqual(service.list_user_memory("user_1")["memoryCards"], [])
        self.assertEqual(len(service.list_user_memory("user_1", include_deleted=True)["memoryCards"]), 1)

    def test_hides_deprecated_generic_relationship_memory(self) -> None:
        repository = FakeMemoryRepository()
        service = MemoryService(repository)
        service.accept_candidate(
            "user_1",
            MemoryCandidate(
                scope="idle",
                owner_type="agent_pair",
                owner_id="agent_1:agent_2",
                memory_type="relationship",
                summary="Nora and Vale shared another idle interaction.",
                source_message_ids=["message_1", "message_2"],
                source_sender_types=["agent"],
                importance_score=0.8,
                confidence=0.9,
            ),
        )

        self.assertEqual(service.list_context_memory("user_1", "idle"), [])
        self.assertEqual(service.list_user_memory("user_1")["memoryCards"], [])
