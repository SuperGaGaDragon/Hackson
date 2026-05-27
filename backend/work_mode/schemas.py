"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["active", "archived"]
MissionStatus = Literal["draft", "running", "paused", "stopping", "stopped", "blocked", "failed", "completed"]
RunStatus = Literal["running", "stopped", "failed", "completed"]
StepStatus = Literal["pending", "running", "failed", "completed", "skipped"]
AutonomyLevel = Literal["supervised"]
EventType = Literal[
    "MISSION_CREATED",
    "MISSION_STARTED",
    "STEP_STARTED",
    "SUMMARY",
    "WARNING",
    "RAW_LOG",
    "PRODUCT_UPDATED",
    "STEP_COMPLETED",
    "MISSION_STOP_REQUESTED",
    "MISSION_STOPPED",
    "MISSION_COMPLETED",
    "MISSION_FAILED",
]


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    repo_path: str = Field(min_length=1, max_length=2000, alias="repoPath")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "repo_path")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value


class MissionCreateRequest(BaseModel):
    project_id: str = Field(min_length=1, alias="projectId")
    title: str = Field(min_length=1, max_length=160)
    goal: str = Field(min_length=1, max_length=8000)
    lead_employee_id: str = Field(default="employee_default_lead", min_length=1, max_length=120, alias="leadEmployeeId")
    supporting_employee_ids: list[str] = Field(default_factory=list, alias="supportingEmployeeIds")
    autonomy_level: AutonomyLevel = Field(default="supervised", alias="autonomyLevel")
    max_iterations: int = Field(default=1, ge=1, le=20, alias="maxIterations")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("project_id", "title", "goal", "lead_employee_id")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value

    @field_validator("supporting_employee_ids")
    @classmethod
    def strip_supporting_employee_ids(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class MissionStartRequest(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)


class MissionStopRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=1000)

    @field_validator("reason")
    @classmethod
    def strip_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    name: str
    repo_path: str = Field(alias="repoPath")
    status: ProjectStatus
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class MissionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    project_id: str = Field(alias="projectId")
    title: str
    goal: str
    status: MissionStatus
    autonomy_level: AutonomyLevel = Field(alias="autonomyLevel")
    max_iterations: int = Field(alias="maxIterations")
    lead_employee_id: str = Field(alias="leadEmployeeId")
    lead_employee_name: str = Field(alias="leadEmployeeName")
    supporting_employee_ids: list[str] = Field(alias="supportingEmployeeIds")
    current_step: str | None = Field(default=None, alias="currentStep")
    last_error: str | None = Field(default=None, alias="lastError")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class RunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    status: RunStatus
    iteration: int
    started_at: datetime = Field(alias="startedAt")
    ended_at: datetime | None = Field(default=None, alias="endedAt")
    metadata: dict[str, Any]


class StepResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    run_id: str = Field(alias="runId")
    sequence: int
    title: str
    status: StepStatus
    started_at: datetime | None = Field(default=None, alias="startedAt")
    ended_at: datetime | None = Field(default=None, alias="endedAt")
    metadata: dict[str, Any]


class EventResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    run_id: str | None = Field(default=None, alias="runId")
    step_id: str | None = Field(default=None, alias="stepId")
    sequence: int
    type: EventType
    title: str
    message: str
    payload: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")


class MissionDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project: ProjectResponse
    mission: MissionResponse
    active_run: RunResponse | None = Field(default=None, alias="activeRun")
    latest_run: RunResponse | None = Field(default=None, alias="latestRun")
    events: list[EventResponse]
