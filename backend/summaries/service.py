"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any, Protocol

from fastapi import HTTPException, status

from conversations.model import now_utc
from context.schemas import ConversationSummary
from summaries.model import public_summary
from summaries.schemas import SummaryCreateRequest


class SummaryRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_summary(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def get_latest_summary(
        self,
        user_id: str,
        conversation_id: str,
        summary_type: str,
    ) -> dict[str, Any] | None: ...


class SummaryService:
    """Business rules for rebuildable conversation summaries."""

    def __init__(self, repository: SummaryRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def create_summary(self, user_id: str, payload: SummaryCreateRequest) -> dict[str, Any]:
        if not payload.source_message_start_id or not payload.source_message_end_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="summary_requires_source_message_range",
            )
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "conversation_id": payload.conversation_id,
            "summary_type": payload.summary_type,
            "content": payload.content,
            "source_message_start_id": payload.source_message_start_id,
            "source_message_end_id": payload.source_message_end_id,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_summary(self.repository.create_summary(document))

    def get_latest_summary(
        self,
        user_id: str,
        conversation_id: str,
        summary_type: str,
    ) -> ConversationSummary | None:
        document = self.repository.get_latest_summary(user_id, conversation_id, summary_type)
        if document is None:
            return None
        return ConversationSummary(
            id=str(document["_id"]),
            summary_type=document["summary_type"],
            content=document["content"],
        )
