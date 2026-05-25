"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Protocol

from fastapi import HTTPException, status

from conversations.model import now_utc, public_conversation, public_message
from conversations.schemas import ConversationCreateRequest, MessageAppendRequest

DEFAULT_AGENT_SLOTS = ["agent_1", "agent_2"]


class ConversationRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_conversation(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_conversation(self, conversation_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_conversations(
        self,
        user_id: str,
        mode: str | None,
        status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]: ...
    def find_active_idle_conversation(self, user_id: str) -> dict[str, Any] | None: ...
    def append_message(self, conversation: dict[str, Any], message: dict[str, Any]) -> dict[str, Any]: ...
    def list_messages(
        self,
        conversation_id: str,
        user_id: str,
        after_sequence: int | None,
        created_after: datetime | None,
        created_before: datetime | None,
        limit: int,
    ) -> list[dict[str, Any]]: ...


class ConversationService:
    """Product business rules for conversation containers and messages."""

    def __init__(self, repository: ConversationRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def create_conversation(self, user_id: str, payload: ConversationCreateRequest) -> dict[str, Any]:
        timestamp = now_utc()
        self._validate_parent(user_id, payload.mode, payload.parent_conversation_id)
        document = {
            "user_id": user_id,
            "mode": payload.mode,
            "status": "active",
            "title": payload.title,
            "participant_slots": payload.participant_slots or DEFAULT_AGENT_SLOTS,
            "parent_conversation_id": payload.parent_conversation_id,
            "message_count": 0,
            "last_message_at": None,
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_conversation(self.repository.create_conversation(document))

    def list_conversations(
        self,
        user_id: str,
        mode: str | None,
        conversation_status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        safe_limit = min(max(limit, 1), 100)
        documents = self.repository.list_conversations(user_id, mode, conversation_status, safe_limit)
        return [public_conversation(document) for document in documents]

    def get_conversation(self, user_id: str, conversation_id: str) -> dict[str, Any]:
        conversation = self.repository.find_conversation(conversation_id, user_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation_not_found")
        return public_conversation(conversation)

    def get_or_create_active_idle(self, user_id: str) -> dict[str, Any]:
        existing = self.repository.find_active_idle_conversation(user_id)
        if existing is not None:
            return public_conversation(existing)
        payload = ConversationCreateRequest(
            mode="idle",
            title="Idle",
            participant_slots=DEFAULT_AGENT_SLOTS,
            metadata={"created_by": "get_or_create_active_idle"},
        )
        return self.create_conversation(user_id, payload)

    def append_message(
        self,
        user_id: str,
        conversation_id: str,
        payload: MessageAppendRequest,
    ) -> dict[str, Any]:
        conversation = self.repository.find_conversation(conversation_id, user_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation_not_found")
        self._validate_sender(payload)
        timestamp = now_utc()
        message = {
            "conversation_id": conversation["_id"],
            "user_id": user_id,
            "mode": conversation["mode"],
            "sender_type": payload.sender_type,
            "sender_id": payload.sender_id,
            "sender_slot": payload.sender_slot,
            "role": payload.role,
            "content": payload.content,
            "content_type": payload.content_type,
            "metadata": payload.metadata,
            "created_at": timestamp,
        }
        return public_message(self.repository.append_message(conversation, message))

    def list_messages(
        self,
        user_id: str,
        conversation_id: str,
        after_sequence: int | None,
        created_after: datetime | None,
        created_before: datetime | None,
        limit: int,
    ) -> dict[str, Any]:
        if self.repository.find_conversation(conversation_id, user_id) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation_not_found")
        if after_sequence is not None and (created_after is not None or created_before is not None):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="use_sequence_or_time_filter_not_both",
            )
        if created_after is not None and created_before is not None and created_after >= created_before:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="created_after_must_be_before_created_before",
            )
        safe_limit = min(max(limit, 1), 100)
        documents = self.repository.list_messages(
            conversation_id,
            user_id,
            after_sequence,
            created_after,
            created_before,
            safe_limit,
        )
        messages = [public_message(document) for document in documents]
        next_after = None
        if after_sequence is not None:
            next_after = messages[-1]["sequence"] if len(messages) == safe_limit else None
        return {"messages": messages, "nextAfterSequence": next_after}

    def _validate_parent(
        self,
        user_id: str,
        mode: str,
        parent_conversation_id: str | None,
    ) -> None:
        if mode == "companion_1":
            if parent_conversation_id is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="companion_1_requires_parent_conversation",
                )
            parent = self.repository.find_conversation(parent_conversation_id, user_id)
            if parent is None or parent["mode"] != "idle":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="parent_conversation_must_be_idle",
                )

    def _validate_sender(self, payload: MessageAppendRequest) -> None:
        if payload.sender_type == "agent" and payload.sender_slot is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="agent_message_requires_sender_slot",
            )
        if payload.sender_slot is not None and payload.sender_type != "agent":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="sender_slot_only_allowed_for_agent",
            )
