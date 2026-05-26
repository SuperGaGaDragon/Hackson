"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from conversations.schemas import ConversationCreateRequest
from conversations.service import ConversationService
from conversations.tests.test_conversation_service import FakeConversationRepository
from tasks.schemas import TaskCreateRequest
from tasks.service import TaskService


class FakeTaskRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.tasks: dict[str, dict[str, Any]] = {}
        self.tool_traces: list[dict[str, Any]] = []
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create_task(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"task_{self.next_id}"
        self.next_id += 1
        self.tasks[row["_id"]] = row
        return row

    def find_task(self, task_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.tasks.get(task_id)
        if row is None or row["user_id"] != user_id:
            return None
        return row

    def list_tasks(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return [row for row in self.tasks.values() if row["user_id"] == user_id][:limit]

    def create_tool_trace(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = f"trace_{len(self.tool_traces) + 1}"
        self.tool_traces.append(row)
        return row


class TaskServiceTest(TestCase):
    def test_create_task_creates_work_conversation_and_state_snapshot(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        task_repository = FakeTaskRepository()
        service = TaskService(task_repository, conversation_service)

        task = service.create_task(
            "user_1",
            TaskCreateRequest(objective="Prepare a demo checklist."),
        )
        snapshot = service.get_task_state("user_1", task["id"])
        conversation = conversation_service.get_conversation("user_1", task["conversationId"])

        self.assertTrue(task_repository.indexes_ready)
        self.assertEqual(conversation["mode"], "work")
        self.assertEqual(snapshot["objective"], "Prepare a demo checklist.")
        self.assertEqual(snapshot["status"], "active")

    def test_create_tool_trace_is_task_scoped(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        service = TaskService(FakeTaskRepository(), conversation_service)
        task = service.create_task("user_1", TaskCreateRequest(objective="Ship work mode."))

        trace = service.create_tool_trace(
            "user_1",
            task["id"],
            tool_name="codex",
            input_summary="inspect files",
            output_summary="found task module",
            status_value="succeeded",
        )

        self.assertEqual(trace["taskId"], task["id"])
        self.assertEqual(trace["toolName"], "codex")
        self.assertEqual(trace["status"], "succeeded")

    def test_task_lookup_requires_owner(self) -> None:
        conversation_service = ConversationService(FakeConversationRepository())
        service = TaskService(FakeTaskRepository(), conversation_service)
        task = service.create_task("user_1", TaskCreateRequest(objective="Private task."))

        with self.assertRaises(Exception):
            service.get_task_state("user_2", task["id"])
