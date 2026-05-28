"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MemoryScope = Literal["idle", "companion", "work"]
MemoryOwnerType = Literal["user", "agent", "agent_pair", "task", "shared_world"]
MemoryType = Literal["fact", "preference", "episode", "relationship", "reflection", "skill", "task"]
MemoryStatus = Literal["active", "disabled", "rejected", "archived", "deleted"]
SourceSenderType = Literal["user", "agent", "system", "tool"]


class MemoryCandidate(BaseModel):
    scope: MemoryScope
    owner_type: MemoryOwnerType
    owner_id: str
    memory_type: MemoryType
    summary: str = Field(min_length=1, max_length=4000)
    source_message_ids: list[str] = Field(default_factory=list)
    source_sender_types: list[SourceSenderType] = Field(default_factory=list)
    importance_score: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("summary")
    @classmethod
    def strip_summary(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("memory_summary_required")
        return value


class MemoryCardResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    scope: MemoryScope
    owner_type: MemoryOwnerType = Field(alias="ownerType")
    owner_id: str = Field(alias="ownerId")
    memory_type: MemoryType = Field(alias="memoryType")
    summary: str
    source_message_ids: list[str] = Field(alias="sourceMessageIds")
    importance_score: float = Field(alias="importanceScore")
    confidence: float
    status: MemoryStatus
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class MemoryCardListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    memory_cards: list[MemoryCardResponse] = Field(default_factory=list, alias="memoryCards")


class MemoryCardUpdateRequest(BaseModel):
    status: MemoryStatus


class MemoryCardDeleteResponse(BaseModel):
    deleted_memory_card: bool = Field(alias="deletedMemoryCard")
