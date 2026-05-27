"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import os
import time
from typing import Any, Protocol

from core.database import get_database
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage
from work_mode.repository import WorkModeRepository
from work_mode.service import WorkModeService


class MissionRunnerProtocol(Protocol):
    def run(self, context: dict[str, Any]) -> dict[str, Any]: ...


class MissionWorker:
    """Single-run Work Mode worker that emits Mission Runtime events and artifacts."""

    def __init__(
        self,
        service: WorkModeService,
        event_delay_seconds: float = 0.0,
        runner: MissionRunnerProtocol | None = None,
    ):
        self.service = service
        self.event_delay_seconds = max(event_delay_seconds, 0.0)
        self.runner = runner or ModelMissionRunner()

    def run_v0_mission(self, user_id: str, mission_id: str, run_id: str) -> None:
        try:
            self._run(user_id, mission_id, run_id)
        except MissionStopped:
            return
        except Exception as exc:
            self.service.mark_mission_failed(user_id, mission_id, run_id, str(exc))

    def _run(self, user_id: str, mission_id: str, run_id: str) -> None:
        if self.service.should_stop(user_id, mission_id):
            self.service.mark_mission_stopped(user_id, mission_id, run_id, step_id=None)
            return

        detail = self.service.get_mission_detail(user_id, mission_id)
        mission = detail["mission"]
        project = detail["project"]
        step = self.service.create_step(user_id, mission_id, run_id, "Generate")
        run = {"_id": run_id}
        employee = _employee_payload(mission)

        self._event(user_id, mission_id, run, step, "STEP_STARTED", "Generate", "Generating artifact.", {"employee": employee})
        self._pause_for_visibility()
        self._stop_if_needed(user_id, mission_id, run_id, str(step["_id"]))

        result = self.runner.run({"project": project, "mission": mission, "runId": run_id, "employee": employee})

        self._event(
            user_id,
            mission_id,
            run,
            step,
            "RAW_LOG",
            "Log",
            "Runner produced artifact.",
            {
                "employee": employee,
                "stream": "stdout",
                "text": f"{result.get('metadata', {}).get('runner', 'model')} produced {result['kind']} artifact.",
            },
        )
        self._pause_for_visibility()
        self._stop_if_needed(user_id, mission_id, run_id, str(step["_id"]))

        artifact = self.service.create_artifact(
            user_id,
            mission_id,
            run_id,
            result["kind"],
            result["title"],
            result["content"],
            result.get("metadata", {}),
        )
        self._event(
            user_id,
            mission_id,
            run,
            step,
            "PRODUCT_UPDATED",
            "Product",
            artifact["title"],
            {
                "employee": employee,
                "artifactId": artifact["id"],
                "kind": artifact["kind"],
                "summary": _preview(artifact["content"]),
                "changedFiles": [],
                "tests": "not_run",
            },
        )
        completed_step = self.service.complete_step(user_id, str(step["_id"]))
        self._event(
            user_id,
            mission_id,
            run,
            completed_step,
            "STEP_COMPLETED",
            "Step done",
            "Artifact generated.",
            {"status": "completed"},
        )
        self.service.mark_mission_completed(user_id, mission_id, run_id, str(completed_step["_id"]))

    def _pause_for_visibility(self) -> None:
        if self.event_delay_seconds > 0:
            time.sleep(self.event_delay_seconds)

    def _stop_if_needed(self, user_id: str, mission_id: str, run_id: str, step_id: str) -> None:
        if self.service.should_stop(user_id, mission_id):
            self.service.mark_mission_stopped(user_id, mission_id, run_id, step_id)
            raise MissionStopped()

    def _event(
        self,
        user_id: str,
        mission_id: str,
        run: dict[str, Any],
        step: dict[str, Any],
        event_type: str,
        title: str,
        message: str,
        payload: dict[str, Any],
    ) -> None:
        mission = self.service._require_mission(user_id, mission_id)
        self.service.append_event(user_id, mission, run=run, step=step, event_type=event_type, title=title, message=message, payload=payload)


class MissionStopped(Exception):
    """Internal control-flow marker for cooperative V0 stop."""


class ModelMissionRunner:
    """Generate one text artifact through the platform model runtime."""

    def __init__(self, model_runtime: ModelRuntime | None = None):
        self.model_runtime = model_runtime or ModelRuntime(
            config_repository=ModelRuntimeConfigRepository(),
            client=OpenAICompatibleClient(),
        )

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        mission = context["mission"]
        project = context["project"]
        employee = context["employee"]
        response = self.model_runtime.generate(
            ModelGenerateRequest(
                messages=[
                    RuntimeMessage(
                        role="system",
                        content=(
                            "You are the Work Mode lead agent. Produce the requested artifact directly. "
                            "Do not describe the UI or claim external actions. Write concise, usable output."
                        ),
                    ),
                    RuntimeMessage(
                        role="user",
                        content=(
                            f"Project: {project['name']}\n"
                            f"Mission: {mission['title']}\n"
                            f"Goal: {mission['goal']}\n"
                            f"Lead agent: {employee['name']} ({employee['role']})\n"
                            "Return the artifact content only."
                        ),
                    ),
                ],
                max_output_tokens=1400,
                temperature=0.4,
            )
        )
        return {
            "kind": "text",
            "title": mission["title"],
            "content": response.text,
            "metadata": {
                "runner": "model_runtime",
                "modelName": response.model_name,
                "provider": response.provider,
            },
        }


def _employee_payload(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission.get("leadEmployeeId") or mission.get("lead_employee_id") or "employee_default_lead",
        "name": mission.get("leadEmployeeName") or mission.get("lead_employee_name") or "Lead",
        "role": mission.get("leadEmployeeRole") or mission.get("lead_employee_role") or "Mission lead",
    }


def _preview(content: str, limit: int = 320) -> str:
    content = " ".join(content.split())
    if len(content) <= limit:
        return content
    return f"{content[:limit].rstrip()}..."


def run_v0_mission_from_database(user_id: str, mission_id: str, run_id: str) -> None:
    """Run a V0 mission worker using the configured MongoDB database."""
    service = WorkModeService(WorkModeRepository(get_database()))
    MissionWorker(service, event_delay_seconds=_event_delay_seconds()).run_v0_mission(user_id, mission_id, run_id)


def _event_delay_seconds() -> float:
    raw_value = os.getenv("HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS", "0")
    try:
        return max(float(raw_value), 0.0)
    except ValueError:
        return 0.0
