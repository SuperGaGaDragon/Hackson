"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

import json
from collections.abc import Callable, Iterator

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse

from core.database import get_database
from users.auth import get_current_user_id
from users.repository import UserRepository
from users.service import UserService
from work_mode.repository import WorkModeRepository
from work_mode.schemas import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EventResponse,
    MissionAnswerRequest,
    MissionCreateRequest,
    MissionDetailResponse,
    MissionEvaluateRequest,
    MissionResponse,
    MissionStartRequest,
    MissionStopRequest,
    ProjectCreateRequest,
    ProjectEmployeeAddRequest,
    ProjectEmployeeResponse,
    ProjectResponse,
)
from work_mode.evaluator import EvaluatorRuntime
from work_mode.service import WorkModeService
from work_mode.worker import launch_v1_mission_daemon

router = APIRouter()

TERMINAL_STREAM_STATUSES = {"completed", "failed", "stopped", "blocked"}


def get_work_mode_service() -> WorkModeService:
    return WorkModeService(WorkModeRepository(get_database()))


def get_evaluator_runtime(service: WorkModeService = Depends(get_work_mode_service)) -> EvaluatorRuntime:
    return EvaluatorRuntime(service)


def get_user_service() -> UserService:
    return UserService(UserRepository(get_database()))


def get_work_mode_worker_launcher() -> Callable[[str, str, str], None]:
    return launch_v1_mission_daemon


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> dict:
    return service.create_project(current_user_id, payload)


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> list[dict]:
    return service.list_projects(current_user_id, limit)


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> dict:
    return service.create_employee(current_user_id, payload)


@router.get("/employees", response_model=list[EmployeeResponse])
def list_employees(
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> list[dict]:
    return service.list_employees(current_user_id, limit)


@router.post(
    "/projects/{project_id}/employees",
    response_model=ProjectEmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_project_employee(
    project_id: str,
    payload: ProjectEmployeeAddRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> dict:
    return service.add_project_employee(current_user_id, project_id, payload)


@router.get("/projects/{project_id}/employees", response_model=list[ProjectEmployeeResponse])
def list_project_employees(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> list[dict]:
    return service.list_project_employees(current_user_id, project_id, limit)


@router.post("/missions", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(
    payload: MissionCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
    user_service: UserService = Depends(get_user_service),
) -> dict:
    current_user = user_service.get_user(current_user_id)
    return service.create_mission(current_user_id, payload, current_user.get("agentProfiles", []))


@router.get("/projects/{project_id}/missions", response_model=list[MissionResponse])
def list_project_missions(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> list[dict]:
    return service.list_missions(current_user_id, project_id, limit)


@router.get("/missions/{mission_id}", response_model=MissionDetailResponse)
def get_mission(
    mission_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> dict:
    return service.get_mission_detail(current_user_id, mission_id)


@router.post("/missions/{mission_id}/start", response_model=MissionDetailResponse)
def start_mission(
    mission_id: str,
    payload: MissionStartRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
    worker_launcher: Callable[[str, str, str], None] = Depends(get_work_mode_worker_launcher),
) -> dict:
    detail = service.start_mission(current_user_id, mission_id, payload)
    active_run = detail.get("activeRun")
    if active_run is not None:
        worker_launcher(current_user_id, mission_id, active_run["id"])
    return detail


@router.post("/missions/{mission_id}/stop", response_model=MissionDetailResponse)
def stop_mission(
    mission_id: str,
    payload: MissionStopRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> dict:
    return service.stop_mission(current_user_id, mission_id, payload)


@router.post("/missions/{mission_id}/answer", response_model=MissionDetailResponse)
def answer_mission(
    mission_id: str,
    payload: MissionAnswerRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
    worker_launcher: Callable[[str, str, str], None] = Depends(get_work_mode_worker_launcher),
) -> dict:
    detail = service.answer_mission_input(current_user_id, mission_id, payload)
    active_run = detail.get("activeRun")
    if active_run is not None:
        worker_launcher(current_user_id, mission_id, active_run["id"])
    return detail


@router.post("/missions/{mission_id}/evaluate", response_model=MissionDetailResponse)
def evaluate_mission(
    mission_id: str,
    payload: MissionEvaluateRequest,
    current_user_id: str = Depends(get_current_user_id),
    evaluator: EvaluatorRuntime = Depends(get_evaluator_runtime),
) -> dict:
    return evaluator.evaluate(current_user_id, mission_id, profile=payload.profile)


@router.get("/missions/{mission_id}/events", response_model=list[EventResponse])
def list_mission_events(
    mission_id: str,
    after_sequence: int | None = Query(default=None, ge=0, alias="afterSequence"),
    limit: int = Query(default=100, ge=1, le=500),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> list[dict]:
    return service.list_events(current_user_id, mission_id, after_sequence, limit)


@router.get("/missions/{mission_id}/events/stream")
def stream_mission_events(
    mission_id: str,
    after_sequence: int | None = Query(default=None, ge=0, alias="afterSequence"),
    current_user_id: str = Depends(get_current_user_id),
    service: WorkModeService = Depends(get_work_mode_service),
) -> StreamingResponse:
    service.get_mission_detail(current_user_id, mission_id)
    return StreamingResponse(
        _mission_event_stream(service, current_user_id, mission_id, after_sequence),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _mission_event_stream(
    service: WorkModeService,
    user_id: str,
    mission_id: str,
    after_sequence: int | None,
    poll_seconds: float = 1.0,
    ping_seconds: float = 15.0,
    max_idle_polls: int | None = None,
) -> Iterator[str]:
    cursor = max(after_sequence or 0, 0)
    idle_polls = 0
    seconds_since_ping = 0.0
    while True:
        events = service.list_events(user_id, mission_id, after_sequence=cursor, limit=100)
        for event in events:
            cursor = max(cursor, event["sequence"])
            yield _sse_message("work_event", event, event_id=str(event["sequence"]))
        detail = service.get_mission_detail(user_id, mission_id)
        if detail["mission"]["status"] in TERMINAL_STREAM_STATUSES:
            return
        if events:
            idle_polls = 0
            seconds_since_ping = 0.0
            continue
        idle_polls += 1
        seconds_since_ping += poll_seconds
        if seconds_since_ping >= ping_seconds:
            yield _sse_message("ping", {"status": "ok"})
            seconds_since_ping = 0.0
        if max_idle_polls is not None and idle_polls >= max_idle_polls:
            return
        import time

        time.sleep(max(poll_seconds, 0.0))


def _sse_message(event: str, data: dict, event_id: str | None = None) -> str:
    parts = []
    if event_id is not None:
        parts.append(f"id: {event_id}")
    parts.append(f"event: {event}")
    body = json.dumps(data, ensure_ascii=False, default=str)
    for line in body.splitlines() or [""]:
        parts.append(f"data: {line}")
    return "\n".join(parts) + "\n\n"
