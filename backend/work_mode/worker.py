"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import os
import time
from typing import Any

from core.database import get_database
from work_mode.repository import WorkModeRepository
from work_mode.service import WorkModeService, DEFAULT_LEAD_EMPLOYEE


class MissionWorker:
    """Deterministic V0 worker that emits Mission Runtime events."""

    def __init__(self, service: WorkModeService, event_delay_seconds: float = 0.0):
        self.service = service
        self.event_delay_seconds = max(event_delay_seconds, 0.0)

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
        step = self.service.create_step(user_id, mission_id, run_id, "Inspect mission")
        run = {"_id": run_id}

        self._event(user_id, mission_id, run, step, "STEP_STARTED", "Inspect", "Inspecting mission state.", {})
        self._pause_for_visibility()
        self._stop_if_needed(user_id, mission_id, run_id, str(step["_id"]))

        self._event(
            user_id,
            mission_id,
            run,
            step,
            "SUMMARY",
            "Summary",
            "Mission loaded.",
            {
                "employee": DEFAULT_LEAD_EMPLOYEE,
                "items": [
                    f"Project: {project['name']}",
                    f"Repo: {project['repoPath']}",
                    f"Goal: {mission['goal']}",
                ]
            },
        )
        self._pause_for_visibility()
        self._stop_if_needed(user_id, mission_id, run_id, str(step["_id"]))

        self._event(
            user_id,
            mission_id,
            run,
            step,
            "RAW_LOG",
            "Log",
            "V0 worker inspected mission state.",
            {"employee": DEFAULT_LEAD_EMPLOYEE, "stream": "stdout", "text": "V0 worker inspected mission state."},
        )
        self._pause_for_visibility()
        self._stop_if_needed(user_id, mission_id, run_id, str(step["_id"]))

        self._event(
            user_id,
            mission_id,
            run,
            step,
            "PRODUCT_UPDATED",
            "Product",
            "V0 Mission Runtime completed.",
            {
                "employee": DEFAULT_LEAD_EMPLOYEE,
                "kind": "mission_result",
                "summary": "V0 Mission Runtime completed a deterministic worker run.",
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
            "Inspect mission completed.",
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
