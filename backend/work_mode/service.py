"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any, Protocol

from fastapi import HTTPException, status

from agents.catalog import normalize_user_agent_profiles
from conversations.model import now_utc
from work_mode.model import (
    public_artifact,
    public_employee,
    public_event,
    public_mission,
    public_product,
    public_project,
    public_project_employee,
    public_run,
    public_step,
    public_work_window,
)
from work_mode.schemas import (
    EmployeeCreateRequest,
    MissionCreateRequest,
    MissionStartRequest,
    MissionStopRequest,
    ProjectCreateRequest,
    ProjectEmployeeAddRequest,
)

DEFAULT_LEAD_EMPLOYEE = {
    "id": "employee_default_lead",
    "name": "Lead",
    "role": "Mission lead",
}
DEFAULT_PROJECT_REPO_PATH = ""
USER_AGENT_LEAD_IDS = {"agent_1", "agent_2"}


class WorkModeRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_project(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_project(self, project_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_projects(self, user_id: str, limit: int) -> list[dict[str, Any]]: ...
    def create_employee(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_employee(self, employee_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_employees(self, user_id: str, limit: int) -> list[dict[str, Any]]: ...
    def add_project_employee(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_project_employee(self, project_id: str, employee_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_project_employees(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]: ...
    def create_mission(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_mission(self, mission_id: str, user_id: str) -> dict[str, Any] | None: ...
    def list_missions(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]: ...
    def update_mission(self, mission_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None: ...
    def create_run(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_active_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None: ...
    def find_latest_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None: ...
    def update_run(self, run_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None: ...
    def create_step(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def update_step(self, step_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None: ...
    def create_artifact(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def list_artifacts(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]: ...
    def create_product(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_product(self, product_id: str, user_id: str) -> dict[str, Any] | None: ...
    def update_product(self, product_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None: ...
    def list_products(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]: ...
    def create_work_window(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def update_work_window(self, window_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None: ...
    def list_work_windows(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]: ...
    def next_event_sequence(self, mission_id: str) -> int: ...
    def create_event(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def list_events(self, user_id: str, mission_id: str, after_sequence: int | None, limit: int) -> list[dict[str, Any]]: ...


class WorkModeService:
    """Business rules for Work Mode Projects, Missions, Runs, Steps, and Events."""

    def __init__(self, repository: WorkModeRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def create_project(self, user_id: str, payload: ProjectCreateRequest) -> dict[str, Any]:
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "name": payload.name,
            "repo_path": payload.repo_path or DEFAULT_PROJECT_REPO_PATH,
            "status": "active",
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_project(self.repository.create_project(document))

    def list_projects(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = min(max(limit, 1), 100)
        return [public_project(row) for row in self.repository.list_projects(user_id, safe_limit)]

    def create_employee(self, user_id: str, payload: EmployeeCreateRequest) -> dict[str, Any]:
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "name": payload.name,
            "role": payload.role,
            "personality": payload.personality,
            "experience": payload.experience,
            "skills": payload.skills,
            "permissions": payload.permissions,
            "default_output_style": payload.default_output_style,
            "status": "active",
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_employee(self.repository.create_employee(document))

    def list_employees(self, user_id: str, limit: int = 50) -> list[dict[str, Any]]:
        safe_limit = min(max(limit, 1), 100)
        return [public_employee(row) for row in self.repository.list_employees(user_id, safe_limit)]

    def add_project_employee(self, user_id: str, project_id: str, payload: ProjectEmployeeAddRequest) -> dict[str, Any]:
        project = self._require_project(user_id, project_id)
        employee = self._require_employee(user_id, payload.employee_id)
        existing = self.repository.find_project_employee(str(project["_id"]), str(employee["_id"]), user_id)
        if existing is not None:
            return public_project_employee(existing, employee)
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "project_id": project["_id"],
            "employee_id": employee["_id"],
            "role_on_project": payload.role_on_project,
            "is_lead_default": payload.is_lead_default,
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_project_employee(self.repository.add_project_employee(document), employee)

    def list_project_employees(self, user_id: str, project_id: str, limit: int = 50) -> list[dict[str, Any]]:
        project = self._require_project(user_id, project_id)
        safe_limit = min(max(limit, 1), 100)
        rows = self.repository.list_project_employees(user_id, str(project["_id"]), safe_limit)
        employees = {str(row["_id"]): row for row in self.repository.list_employees(user_id, 500)}
        return [
            public_project_employee(row, employees[str(row["employee_id"])])
            for row in rows
            if str(row["employee_id"]) in employees
        ]

    def create_mission(
        self,
        user_id: str,
        payload: MissionCreateRequest,
        agent_profiles: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        project = self._require_project(user_id, payload.project_id)
        lead_employee = self._mission_lead_employee(
            user_id,
            str(project["_id"]),
            payload.lead_employee_id,
            agent_profiles,
        )
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "project_id": project["_id"],
            "title": payload.title,
            "goal": payload.goal,
            "status": "draft",
            "autonomy_level": payload.autonomy_level,
            "max_iterations": payload.max_iterations,
            "lead_employee_id": lead_employee["id"],
            "lead_employee_name": lead_employee["name"],
            "lead_employee_role": lead_employee["role"],
            "supporting_employee_ids": payload.supporting_employee_ids,
            "current_step": None,
            "last_error": None,
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        mission = self.repository.create_mission(document)
        self.append_event(
            user_id,
            mission,
            run=None,
            step=None,
            event_type="MISSION_CREATED",
            title="Mission created",
            message=mission["title"],
            payload={"projectId": str(project["_id"]), "employee": _employee_payload(mission)},
        )
        return public_mission(mission)

    def list_missions(self, user_id: str, project_id: str, limit: int = 50) -> list[dict[str, Any]]:
        self._require_project(user_id, project_id)
        safe_limit = min(max(limit, 1), 100)
        return [public_mission(row) for row in self.repository.list_missions(user_id, project_id, safe_limit)]

    def get_mission_detail(self, user_id: str, mission_id: str) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        project = self._require_project(user_id, str(mission["project_id"]))
        active_run = self.repository.find_active_run(str(mission["_id"]), user_id)
        latest_run = active_run or self.repository.find_latest_run(str(mission["_id"]), user_id)
        events = self.repository.list_events(user_id, str(mission["_id"]), after_sequence=None, limit=100)
        artifacts = self.repository.list_artifacts(user_id, str(mission["_id"]), limit=20)
        products = self.repository.list_products(user_id, str(mission["_id"]), limit=50)
        work_windows = self.repository.list_work_windows(user_id, str(mission["_id"]), limit=100)
        return {
            "project": public_project(project),
            "mission": public_mission(mission),
            "activeRun": public_run(active_run) if active_run is not None else None,
            "latestRun": public_run(latest_run) if latest_run is not None else None,
            "events": [public_event(event) for event in events],
            "artifacts": [public_artifact(artifact) for artifact in artifacts],
            "products": [public_product(product) for product in products],
            "workWindows": [public_work_window(window) for window in work_windows],
        }

    def start_mission(self, user_id: str, mission_id: str, payload: MissionStartRequest) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        if mission["status"] in {"running", "stopping"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mission_already_running")
        if mission["status"] not in {"draft", "paused", "stopped", "blocked", "failed", "completed"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mission_cannot_start")
        timestamp = now_utc()
        mission = self._update_mission(
            user_id,
            mission_id,
            {
                "status": "running",
                "current_step": "Starting",
                "last_error": None,
                "updated_at": timestamp,
            },
        )
        run = self.repository.create_run(
            {
                "user_id": user_id,
                "mission_id": mission["_id"],
                "status": "running",
                "iteration": 1,
                "started_at": timestamp,
                "ended_at": None,
                "metadata": payload.metadata,
            }
        )
        self.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="MISSION_STARTED",
            title="Started",
            message="Mission started.",
            payload={"maxIterations": mission.get("max_iterations", 1), "employee": _employee_payload(mission)},
        )
        return self.get_mission_detail(user_id, str(mission["_id"]))

    def stop_mission(self, user_id: str, mission_id: str, payload: MissionStopRequest) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        if mission["status"] != "running":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mission_not_running")
        timestamp = now_utc()
        mission = self._update_mission(
            user_id,
            mission_id,
            {
                "status": "stopping",
                "current_step": "Stopping",
                "updated_at": timestamp,
            },
        )
        run = self.repository.find_active_run(str(mission["_id"]), user_id)
        self.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="MISSION_STOP_REQUESTED",
            title="Stop requested",
            message=payload.reason or "User requested stop.",
            payload={"reason": payload.reason, "employee": _employee_payload(mission)},
        )
        if run is None:
            self.mark_mission_stopped(user_id, mission_id, run_id=None, step_id=None)
        return self.get_mission_detail(user_id, mission_id)

    def list_events(
        self,
        user_id: str,
        mission_id: str,
        after_sequence: int | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        self._require_mission(user_id, mission_id)
        safe_limit = min(max(limit, 1), 500)
        events = self.repository.list_events(user_id, mission_id, after_sequence, safe_limit)
        return [public_event(event) for event in events]

    def create_step(self, user_id: str, mission_id: str, run_id: str, title: str) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        timestamp = now_utc()
        step = self.repository.create_step(
            {
                "user_id": user_id,
                "mission_id": mission["_id"],
                "run_id": run_id,
                "sequence": 1,
                "title": title,
                "status": "running",
                "started_at": timestamp,
                "ended_at": None,
                "metadata": {},
            }
        )
        self._update_mission(
            user_id,
            mission_id,
            {"current_step": title, "updated_at": timestamp},
        )
        return step

    def complete_step(self, user_id: str, step_id: str) -> dict[str, Any]:
        timestamp = now_utc()
        step = self.repository.update_step(
            step_id,
            user_id,
            {"status": "completed", "ended_at": timestamp},
        )
        if step is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="step_not_found")
        return step

    def create_artifact(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        kind: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        document = {
            "user_id": user_id,
            "mission_id": mission["_id"],
            "run_id": run_id,
            "kind": kind,
            "title": title,
            "content": content,
            "created_by_employee": _employee_payload(mission),
            "metadata": metadata or {},
            "created_at": now_utc(),
        }
        return public_artifact(self.repository.create_artifact(document))

    def create_product(
        self,
        user_id: str,
        mission_id: str,
        title: str,
        summary: str,
        created_by: dict[str, str],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "mission_id": mission["_id"],
            "title": title,
            "summary": summary,
            "status": "active",
            "artifact_ids": [],
            "latest_artifact_id": None,
            "created_by": created_by,
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_product(self.repository.create_product(document))

    def create_product_artifact(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        product_id: str,
        kind: str,
        title: str,
        content: str,
        summary: str,
        created_by: dict[str, str],
        source_artifact_ids: list[str],
        work_window_id: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        product = self.repository.find_product(product_id, user_id)
        if product is None or str(product["mission_id"]) != str(mission["_id"]):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="product_not_found")
        artifact_metadata = {
            **(metadata or {}),
            "productId": product_id,
            "sourceArtifactIds": source_artifact_ids,
            "workWindowId": work_window_id,
        }
        artifact = self.create_artifact(
            user_id,
            mission_id,
            run_id,
            kind,
            title,
            content,
            artifact_metadata,
        )
        artifact_ids = [str(value) for value in product.get("artifact_ids", [])]
        artifact_ids.append(artifact["id"])
        self.repository.update_product(
            product_id,
            user_id,
            {
                "artifact_ids": artifact_ids,
                "latest_artifact_id": artifact["id"],
                "summary": summary,
                "updated_at": now_utc(),
            },
        )
        return artifact

    def create_work_window(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        agent_slot: str,
        title: str,
        brief: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        mission = self._require_mission(user_id, mission_id)
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "mission_id": mission["_id"],
            "run_id": run_id,
            "agent_slot": agent_slot,
            "title": title,
            "brief": brief,
            "status": "running",
            "result_artifact_id": None,
            "summary": "",
            "metadata": metadata or {},
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_work_window(self.repository.create_work_window(document))

    def complete_work_window(
        self,
        user_id: str,
        window_id: str,
        result_artifact_id: str,
        summary: str,
    ) -> dict[str, Any]:
        timestamp = now_utc()
        window = self.repository.update_work_window(
            window_id,
            user_id,
            {
                "status": "completed",
                "result_artifact_id": result_artifact_id,
                "summary": summary,
                "updated_at": timestamp,
            },
        )
        if window is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="work_window_not_found")
        return public_work_window(window)

    def mark_mission_completed(self, user_id: str, mission_id: str, run_id: str, step_id: str | None) -> None:
        timestamp = now_utc()
        mission = self._update_mission(
            user_id,
            mission_id,
            {"status": "completed", "current_step": "Done", "updated_at": timestamp},
        )
        run = self._update_run(user_id, run_id, {"status": "completed", "ended_at": timestamp})
        self.append_event(
            user_id,
            mission,
            run=run,
            step={"_id": step_id} if step_id else None,
            event_type="MISSION_COMPLETED",
            title="Done",
            message="Mission completed.",
            payload={"status": "completed", "employee": _employee_payload(mission)},
        )

    def fail_step(self, user_id: str, step_id: str) -> dict[str, Any]:
        timestamp = now_utc()
        step = self.repository.update_step(
            step_id,
            user_id,
            {"status": "failed", "ended_at": timestamp},
        )
        if step is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="step_not_found")
        return step

    def mark_mission_failed(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        error: str,
        step_id: str | None = None,
    ) -> None:
        timestamp = now_utc()
        mission = self._update_mission(
            user_id,
            mission_id,
            {"status": "failed", "current_step": "Failed", "last_error": error, "updated_at": timestamp},
        )
        run = self._update_run(user_id, run_id, {"status": "failed", "ended_at": timestamp})
        self.append_event(
            user_id,
            mission,
            run=run,
            step={"_id": step_id} if step_id else None,
            event_type="MISSION_FAILED",
            title="Failed",
            message=error,
            payload={"error": error, "employee": _employee_payload(mission)},
        )

    def mark_mission_stopped(
        self,
        user_id: str,
        mission_id: str,
        run_id: str | None,
        step_id: str | None,
    ) -> None:
        timestamp = now_utc()
        mission = self._update_mission(
            user_id,
            mission_id,
            {"status": "stopped", "current_step": "Stopped", "updated_at": timestamp},
        )
        run = self._update_run(user_id, run_id, {"status": "stopped", "ended_at": timestamp}) if run_id else None
        self.append_event(
            user_id,
            mission,
            run=run,
            step={"_id": step_id} if step_id else None,
            event_type="MISSION_STOPPED",
            title="Stopped",
            message="Mission stopped.",
            payload={"status": "stopped", "employee": _employee_payload(mission)},
        )

    def append_event(
        self,
        user_id: str,
        mission: dict[str, Any],
        run: dict[str, Any] | None,
        step: dict[str, Any] | None,
        event_type: str,
        title: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        sequence = self.repository.next_event_sequence(str(mission["_id"]))
        document = {
            "user_id": user_id,
            "mission_id": mission["_id"],
            "run_id": run["_id"] if run is not None else None,
            "step_id": step["_id"] if step is not None else None,
            "sequence": sequence,
            "type": event_type,
            "title": title,
            "message": message,
            "payload": payload or {},
            "created_at": now_utc(),
        }
        return public_event(self.repository.create_event(document))

    def should_stop(self, user_id: str, mission_id: str) -> bool:
        mission = self._require_mission(user_id, mission_id)
        return mission["status"] == "stopping"

    def _require_project(self, user_id: str, project_id: str) -> dict[str, Any]:
        project = self.repository.find_project(project_id, user_id)
        if project is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project_not_found")
        return project

    def _require_employee(self, user_id: str, employee_id: str) -> dict[str, Any]:
        employee = self.repository.find_employee(employee_id, user_id)
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="employee_not_found")
        return employee

    def _mission_lead_employee(
        self,
        user_id: str,
        project_id: str,
        employee_id: str,
        agent_profiles: list[dict[str, Any]] | None = None,
    ) -> dict[str, str]:
        if employee_id == DEFAULT_LEAD_EMPLOYEE["id"]:
            return DEFAULT_LEAD_EMPLOYEE
        if employee_id in USER_AGENT_LEAD_IDS:
            return _agent_lead_payload(employee_id, agent_profiles)
        employee = self._require_employee(user_id, employee_id)
        membership = self.repository.find_project_employee(project_id, str(employee["_id"]), user_id)
        if membership is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="employee_not_on_project")
        return {"id": str(employee["_id"]), "name": employee["name"], "role": employee["role"]}

    def _require_mission(self, user_id: str, mission_id: str) -> dict[str, Any]:
        mission = self.repository.find_mission(mission_id, user_id)
        if mission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="mission_not_found")
        return mission

    def _update_mission(self, user_id: str, mission_id: str, values: dict[str, Any]) -> dict[str, Any]:
        mission = self.repository.update_mission(mission_id, user_id, values)
        if mission is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="mission_not_found")
        return mission

    def _update_run(self, user_id: str, run_id: str, values: dict[str, Any]) -> dict[str, Any]:
        run = self.repository.update_run(run_id, user_id, values)
        if run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="run_not_found")
        return run


def _employee_payload(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission.get("lead_employee_id", DEFAULT_LEAD_EMPLOYEE["id"]),
        "name": mission.get("lead_employee_name", DEFAULT_LEAD_EMPLOYEE["name"]),
        "role": mission.get("lead_employee_role", DEFAULT_LEAD_EMPLOYEE["role"]),
    }


def _agent_lead_payload(agent_id: str, agent_profiles: list[dict[str, Any]] | None) -> dict[str, str]:
    agents = normalize_user_agent_profiles(agent_profiles)
    agent = next((profile for profile in agents if profile["slot"] == agent_id), None)
    if agent is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="agent_not_available")
    return {
        "id": agent["slot"],
        "name": agent["name"],
        "role": agent["voice"],
    }
