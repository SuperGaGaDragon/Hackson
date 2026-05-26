"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any, Protocol

from fastapi import HTTPException, status

from conversations.model import now_utc
from diary.model import public_diary_entry
from diary.schemas import DiaryEntryCreateRequest


class DiaryRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_diary_entry(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def list_diary_entries(self, user_id: str, agent_id: str | None, limit: int) -> list[dict[str, Any]]: ...


class DiaryService:
    """Business rules for evidence-backed Agent diary entries."""

    def __init__(self, repository: DiaryRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def create_entry(self, user_id: str, payload: DiaryEntryCreateRequest) -> dict[str, Any]:
        if not payload.source_message_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="diary_requires_source_messages",
            )
        document = {
            "user_id": user_id,
            "agent_id": payload.agent_id,
            "content": payload.content,
            "source_message_ids": payload.source_message_ids,
            "created_at": now_utc(),
        }
        return public_diary_entry(self.repository.create_diary_entry(document))

    def list_entries(self, user_id: str, agent_id: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        safe_limit = min(max(limit, 1), 100)
        return [public_diary_entry(row) for row in self.repository.list_diary_entries(user_id, agent_id, safe_limit)]
