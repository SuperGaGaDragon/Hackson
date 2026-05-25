"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ConversationMode = Literal["idle", "companion_1", "companion_2", "work"]
ConversationStatus = Literal["active", "paused", "archived"]
SenderType = Literal["user", "agent", "system", "tool"]
SenderSlot = Literal["agent_1", "agent_2"]
MessageRole = Literal["user", "assistant", "system", "tool"]


class ConversationCreateRequest(BaseModel):
    mode: ConversationMode
    title: str | None = Field(default=None, max_length=120)
    participant_slots: list[SenderSlot] = Field(default_factory=lambda: ["agent_1", "agent_2"])
    parent_conversation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mode: ConversationMode
    status: ConversationStatus
    title: str | None = None
    participant_slots: list[SenderSlot] = Field(alias="participantSlots")
    parent_conversation_id: str | None = Field(default=None, alias="parentConversationId")
    message_count: int = Field(alias="messageCount")
    last_message_at: datetime | None = Field(default=None, alias="lastMessageAt")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class MessageAppendRequest(BaseModel):
    sender_type: SenderType
    sender_id: str | None = None
    sender_slot: SenderSlot | None = None
    role: MessageRole
    content: str = Field(min_length=1)
    content_type: str = Field(default="text", max_length=40)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    conversation_id: str = Field(alias="conversationId")
    user_id: str = Field(alias="userId")
    mode: ConversationMode
    sequence: int
    sender_type: SenderType = Field(alias="senderType")
    sender_id: str | None = Field(default=None, alias="senderId")
    sender_slot: SenderSlot | None = Field(default=None, alias="senderSlot")
    role: MessageRole
    content: str
    content_type: str = Field(alias="contentType")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")


class MessagePageResponse(BaseModel):
    messages: list[MessageResponse]
    next_after_sequence: int | None = Field(default=None, alias="nextAfterSequence")
