"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any, Protocol

from fastapi import HTTPException, status

from conversations.model import now_utc
from conversations.schemas import ConversationCreateRequest
from conversations.service import ConversationService
from tasks.model import public_task, public_tool_trace
from tasks.schemas import TaskCreateRequest


class TaskRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_task(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_task(self, task_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_tasks(self, user_id: str, limit: int) -> list[dict[str, Any]]: ...
    def create_tool_trace(self, document: dict[str, Any]) -> dict[str, Any]: ...


class TaskService:
    """Business rules for minimal Work Mode task state."""

    def __init__(self, repository: TaskRepositoryProtocol, conversation_service: ConversationService):
        self.repository = repository
        self.conversation_service = conversation_service
        self.repository.ensure_indexes()

    def create_task(self, user_id: str, payload: TaskCreateRequest) -> dict[str, Any]:
        conversation = self.conversation_service.create_conversation(
            user_id,
            ConversationCreateRequest(
                mode="work",
                title=payload.objective[:120],
                metadata={"source": "task_create"},
            ),
        )
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "conversation_id": conversation["id"],
            "objective": payload.objective,
            "status": "active",
            "current_phase": "intake",
            "plan_summary": None,
            "progress_summary": None,
            "open_questions": [],
            "blockers": [],
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_task(self.repository.create_task(document))

    def get_task(self, user_id: str, task_id: str) -> dict[str, Any]:
        task = self.repository.find_task(task_id, user_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task_not_found")
        return public_task(task)

    def list_tasks(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = min(max(limit, 1), 100)
        return [public_task(task) for task in self.repository.list_tasks(user_id, safe_limit)]

    def get_task_state(self, user_id: str, task_id: str) -> dict[str, Any]:
        task = self.get_task(user_id, task_id)
        return {
            "task_id": task["id"],
            "objective": task["objective"],
            "status": task["status"],
            "current_phase": task["currentPhase"],
            "plan_summary": task["planSummary"],
            "progress_summary": task["progressSummary"],
            "open_questions": task["openQuestions"],
            "blockers": task["blockers"],
        }

    def create_tool_trace(
        self,
        user_id: str,
        task_id: str,
        tool_name: str,
        input_summary: str,
        output_summary: str | None,
        status_value: str,
    ) -> dict[str, Any]:
        task = self.get_task(user_id, task_id)
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "task_id": task_id,
            "conversation_id": task["conversationId"],
            "tool_name": tool_name,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "status": status_value,
            "created_at": timestamp,
        }
        return public_tool_trace(self.repository.create_tool_trace(document))
