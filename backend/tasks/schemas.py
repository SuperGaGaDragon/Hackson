"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskStatus = Literal["active", "paused", "completed", "archived"]
ToolTraceStatus = Literal["pending", "running", "succeeded", "failed"]


class TaskCreateRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=4000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("objective")
    @classmethod
    def strip_objective(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("task_objective_required")
        return value


class TaskResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    objective: str
    status: TaskStatus
    current_phase: str | None = Field(default=None, alias="currentPhase")
    plan_summary: str | None = Field(default=None, alias="planSummary")
    progress_summary: str | None = Field(default=None, alias="progressSummary")
    open_questions: list[str] = Field(alias="openQuestions")
    blockers: list[str]
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ToolTraceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    task_id: str = Field(alias="taskId")
    conversation_id: str = Field(alias="conversationId")
    tool_name: str = Field(alias="toolName")
    input_summary: str = Field(alias="inputSummary")
    output_summary: str | None = Field(default=None, alias="outputSummary")
    status: ToolTraceStatus
    created_at: datetime = Field(alias="createdAt")
