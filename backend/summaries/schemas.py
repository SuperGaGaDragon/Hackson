"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SummaryType = Literal["session", "idle_scene", "companion", "task"]


class SummaryCreateRequest(BaseModel):
    conversation_id: str = Field(alias="conversationId")
    summary_type: SummaryType = Field(alias="summaryType")
    content: str = Field(min_length=1, max_length=12000)
    source_message_start_id: str | None = Field(default=None, alias="sourceMessageStartId")
    source_message_end_id: str | None = Field(default=None, alias="sourceMessageEndId")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("summary_content_required")
        return value


class SummaryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    summary_type: SummaryType = Field(alias="summaryType")
    content: str
    source_message_start_id: str = Field(alias="sourceMessageStartId")
    source_message_end_id: str = Field(alias="sourceMessageEndId")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
