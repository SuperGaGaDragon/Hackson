"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DiaryEntryCreateRequest(BaseModel):
    agent_id: str = Field(alias="agentId")
    content: str = Field(min_length=1, max_length=12000)
    source_message_ids: list[str] = Field(alias="sourceMessageIds")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("diary_content_required")
        return value


class DiaryEntryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    agent_id: str = Field(alias="agentId")
    content: str
    source_message_ids: list[str] = Field(alias="sourceMessageIds")
    created_at: datetime = Field(alias="createdAt")
