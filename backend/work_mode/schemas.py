"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectStatus = Literal["active", "archived"]
EmployeeStatus = Literal["active", "archived"]
MissionStatus = Literal[
    "draft",
    "running",
    "paused",
    "waiting_input",
    "paused_retryable",
    "stopping",
    "stopped",
    "blocked",
    "failed",
    "completed",
]
RunStatus = Literal["running", "waiting_input", "paused_retryable", "stopped", "failed", "completed", "blocked"]
StepStatus = Literal["pending", "running", "failed", "completed", "skipped"]
AutonomyLevel = Literal["supervised"]
ArtifactKind = Literal[
    "text",
    "log",
    "diff",
    "outline",
    "chapter",
    "draft",
    "revision",
    "final",
    "report",
    "notes",
    "other",
    "mission_result",
]
ProductStatus = Literal["active", "final_candidate", "final", "archived"]
WorkWindowStatus = Literal["queued", "running", "completed", "blocked", "failed", "cancelled"]
EventType = Literal[
    "MISSION_CREATED",
    "MISSION_STARTED",
    "STEP_STARTED",
    "SUMMARY",
    "WARNING",
    "RAW_LOG",
    "MISSION_PLAN_UPDATED",
    "MODEL_TURN_STARTED",
    "MODEL_TURN_HEARTBEAT",
    "MODEL_TURN_COMPLETED",
    "MODEL_TURN_RETRYING",
    "MODEL_TURN_INVALID",
    "TOOL_CALLED",
    "PRODUCT_UPDATED",
    "PRODUCT_INSPECTED",
    "PRODUCT_REVIEWED",
    "WORK_WINDOW_OPENED",
    "WORK_WINDOW_COMPLETED",
    "WORK_WINDOW_BLOCKED",
    "WORK_WINDOW_FAILED",
    "DISCUSSION_WINDOW_OPENED",
    "DISCUSSION_WINDOW_COMPLETED",
    "DISCUSSION_WINDOW_BLOCKED",
    "DISCUSSION_WINDOW_FAILED",
    "WEB_SEARCH_COMPLETED",
    "WEB_SEARCH_FAILED",
    "EVALUATION_STARTED",
    "RELIABILITY_REPORTED",
    "EVALUATION_FAILED",
    "USER_INPUT_REQUESTED",
    "USER_INPUT_RECEIVED",
    "USER_FOLLOWUP_REQUESTED",
    "MISSION_PAUSED_RETRYABLE",
    "MISSION_BLOCKED",
    "STEP_COMPLETED",
    "MISSION_STOP_REQUESTED",
    "MISSION_STOPPED",
    "MISSION_COMPLETED",
    "MISSION_FAILED",
]


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    repo_path: str | None = Field(default=None, max_length=2000, alias="repoPath")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value

    @field_validator("repo_path")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class EmployeeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    role: str = Field(min_length=1, max_length=120)
    personality: str = Field(default="", max_length=2000)
    experience: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    permissions: dict[str, bool] = Field(default_factory=dict)
    default_output_style: str = Field(default="structured_summary", max_length=120, alias="defaultOutputStyle")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name", "role", "default_output_style")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value

    @field_validator("personality")
    @classmethod
    def strip_optional_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("experience", "skills")
    @classmethod
    def strip_text_list(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item.strip()]


class ProjectEmployeeAddRequest(BaseModel):
    employee_id: str = Field(min_length=1, alias="employeeId")
    role_on_project: str = Field(default="Member", min_length=1, max_length=120, alias="roleOnProject")
    is_lead_default: bool = Field(default=False, alias="isLeadDefault")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("employee_id", "role_on_project")
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


class MissionAnswerRequest(BaseModel):
    answer: str = Field(min_length=1, max_length=8000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("answer")
    @classmethod
    def strip_answer(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value


class MissionFollowUpRequest(BaseModel):
    request: str = Field(min_length=1, max_length=8000)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("request")
    @classmethod
    def strip_request(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("required_text_empty")
        return value


class MissionEvaluateRequest(BaseModel):
    profile: Literal["research_reliability_v1"] = "research_reliability_v1"
    mode: Literal["live", "replay"] = "live"


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


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    name: str
    role: str
    personality: str
    experience: list[str]
    skills: list[str]
    permissions: dict[str, bool]
    default_output_style: str = Field(alias="defaultOutputStyle")
    status: EmployeeStatus
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class ProjectEmployeeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    project_id: str = Field(alias="projectId")
    employee_id: str = Field(alias="employeeId")
    employee: EmployeeResponse
    role_on_project: str = Field(alias="roleOnProject")
    is_lead_default: bool = Field(alias="isLeadDefault")
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
    lead_employee_role: str = Field(alias="leadEmployeeRole")
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


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    run_id: str = Field(alias="runId")
    kind: ArtifactKind
    title: str
    content: str
    created_by_employee: dict[str, str] = Field(alias="createdByEmployee")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")


class ProductResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    title: str
    summary: str
    status: ProductStatus
    artifact_ids: list[str] = Field(alias="artifactIds")
    latest_artifact_id: str | None = Field(default=None, alias="latestArtifactId")
    created_by: dict[str, str] = Field(alias="createdBy")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class WorkWindowResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    mission_id: str = Field(alias="missionId")
    run_id: str | None = Field(default=None, alias="runId")
    agent_slot: str = Field(alias="agentSlot")
    title: str
    brief: str
    status: WorkWindowStatus
    result_artifact_id: str | None = Field(default=None, alias="resultArtifactId")
    summary: str
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class MissionDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    project: ProjectResponse
    mission: MissionResponse
    active_run: RunResponse | None = Field(default=None, alias="activeRun")
    latest_run: RunResponse | None = Field(default=None, alias="latestRun")
    events: list[EventResponse]
    artifacts: list[ArtifactResponse]
    products: list[ProductResponse] = Field(default_factory=list)
    work_windows: list[WorkWindowResponse] = Field(default_factory=list, alias="workWindows")
