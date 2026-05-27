"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import os
from typing import Any
from unittest import TestCase

from fastapi import HTTPException

from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, ModelRuntimeConfig
from model_runtime.orchestrator import ModelRuntime
from work_mode.schemas import (
    EmployeeCreateRequest,
    MissionCreateRequest,
    MissionStartRequest,
    MissionStopRequest,
    ProjectCreateRequest,
    ProjectEmployeeAddRequest,
)
from work_mode.service import WorkModeService
from work_mode.worker import MissionWorker, ModelMissionRunner, _event_delay_seconds


class FakeWorkModeRepository:
    def __init__(self) -> None:
        self.indexes_ready = False
        self.projects: dict[str, dict[str, Any]] = {}
        self.employees: dict[str, dict[str, Any]] = {}
        self.project_employees: dict[str, dict[str, Any]] = {}
        self.missions: dict[str, dict[str, Any]] = {}
        self.runs: dict[str, dict[str, Any]] = {}
        self.steps: dict[str, dict[str, Any]] = {}
        self.artifacts: dict[str, dict[str, Any]] = {}
        self.products: dict[str, dict[str, Any]] = {}
        self.work_windows: dict[str, dict[str, Any]] = {}
        self.events: list[dict[str, Any]] = []
        self.event_sequences: dict[str, int] = {}
        self.next_id = 1

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def _id(self, prefix: str) -> str:
        value = f"{prefix}_{self.next_id}"
        self.next_id += 1
        return value

    def create_project(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("project")
        self.projects[row["_id"]] = row
        return row

    def find_project(self, project_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.projects.get(project_id)
        return row if row is not None and row["user_id"] == user_id else None

    def list_projects(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return [row for row in self.projects.values() if row["user_id"] == user_id][:limit]

    def create_employee(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("employee")
        self.employees[row["_id"]] = row
        return row

    def find_employee(self, employee_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.employees.get(employee_id)
        return row if row is not None and row["user_id"] == user_id else None

    def list_employees(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return [row for row in self.employees.values() if row["user_id"] == user_id][:limit]

    def add_project_employee(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("project_employee")
        self.project_employees[row["_id"]] = row
        return row

    def find_project_employee(self, project_id: str, employee_id: str, user_id: str) -> dict[str, Any] | None:
        for row in self.project_employees.values():
            if row["project_id"] == project_id and row["employee_id"] == employee_id and row["user_id"] == user_id:
                return row
        return None

    def list_project_employees(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.project_employees.values()
            if row["user_id"] == user_id and row["project_id"] == project_id
        ][:limit]

    def create_mission(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("mission")
        self.missions[row["_id"]] = row
        self.event_sequences[row["_id"]] = 0
        return row

    def find_mission(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.missions.get(mission_id)
        return row if row is not None and row["user_id"] == user_id else None

    def list_missions(self, user_id: str, project_id: str, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.missions.values()
            if row["user_id"] == user_id and row["project_id"] == project_id
        ][:limit]

    def update_mission(self, mission_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        row = self.find_mission(mission_id, user_id)
        if row is None:
            return None
        row.update(values)
        return row

    def create_run(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("run")
        self.runs[row["_id"]] = row
        return row

    def find_active_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        for row in reversed(list(self.runs.values())):
            if row["mission_id"] == mission_id and row["user_id"] == user_id and row["status"] == "running":
                return row
        return None

    def find_latest_run(self, mission_id: str, user_id: str) -> dict[str, Any] | None:
        for row in reversed(list(self.runs.values())):
            if row["mission_id"] == mission_id and row["user_id"] == user_id:
                return row
        return None

    def update_run(self, run_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        row = self.runs.get(run_id)
        if row is None or row["user_id"] != user_id:
            return None
        row.update(values)
        return row

    def create_step(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("step")
        self.steps[row["_id"]] = row
        return row

    def update_step(self, step_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        row = self.steps.get(step_id)
        if row is None or row["user_id"] != user_id:
            return None
        row.update(values)
        return row

    def create_artifact(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("artifact")
        self.artifacts[row["_id"]] = row
        return row

    def list_artifacts(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.artifacts.values()
            if row["user_id"] == user_id and row["mission_id"] == mission_id
        ][:limit]

    def create_product(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("product")
        self.products[row["_id"]] = row
        return row

    def find_product(self, product_id: str, user_id: str) -> dict[str, Any] | None:
        row = self.products.get(product_id)
        return row if row is not None and row["user_id"] == user_id else None

    def update_product(self, product_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        row = self.find_product(product_id, user_id)
        if row is None:
            return None
        row.update(values)
        return row

    def list_products(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.products.values()
            if row["user_id"] == user_id and row["mission_id"] == mission_id
        ][:limit]

    def create_work_window(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("window")
        self.work_windows[row["_id"]] = row
        return row

    def update_work_window(self, window_id: str, user_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        row = self.work_windows.get(window_id)
        if row is None or row["user_id"] != user_id:
            return None
        row.update(values)
        return row

    def list_work_windows(self, user_id: str, mission_id: str, limit: int) -> list[dict[str, Any]]:
        return [
            row
            for row in self.work_windows.values()
            if row["user_id"] == user_id and row["mission_id"] == mission_id
        ][:limit]

    def next_event_sequence(self, mission_id: str) -> int:
        self.event_sequences[mission_id] = self.event_sequences.get(mission_id, 0) + 1
        return self.event_sequences[mission_id]

    def create_event(self, document: dict[str, Any]) -> dict[str, Any]:
        row = dict(document)
        row["_id"] = self._id("event")
        self.events.append(row)
        return row

    def list_events(self, user_id: str, mission_id: str, after_sequence: int | None, limit: int) -> list[dict[str, Any]]:
        rows = [
            row
            for row in self.events
            if row["user_id"] == user_id
            and row["mission_id"] == mission_id
            and (after_sequence is None or row["sequence"] > after_sequence)
        ]
        return rows[:limit]


class WorkModeServiceTest(TestCase):
    def setUp(self) -> None:
        self.repository = FakeWorkModeRepository()
        self.service = WorkModeService(self.repository)

    def test_create_project_and_mission_records_creation_event(self) -> None:
        project = self.service.create_project(
            "user_1",
            ProjectCreateRequest(name="Cyber1924"),
        )
        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(projectId=project["id"], title="Fix OAuth", goal="Fix Google OAuth."),
        )
        events = self.service.list_events("user_1", mission["id"])

        self.assertTrue(self.repository.indexes_ready)
        self.assertEqual(project["repoPath"], "")
        self.assertEqual(mission["status"], "draft")
        self.assertEqual(mission["leadEmployeeName"], "Lead")
        self.assertEqual(events[0]["type"], "MISSION_CREATED")
        self.assertEqual(events[0]["payload"]["employee"]["id"], "employee_default_lead")

    def test_employee_can_join_project_and_lead_mission(self) -> None:
        project = self.service.create_project(
            "user_1",
            ProjectCreateRequest(name="Cyber1924"),
        )
        employee = self.service.create_employee(
            "user_1",
            EmployeeCreateRequest(
                name="Mira",
                role="Product Designer",
                personality="Calm and visual.",
                experience=["SaaS dashboards"],
                skills=["ux_flow"],
                permissions={"can_edit_files": False, "can_run_codex": False},
            ),
        )
        self.service.add_project_employee(
            "user_1",
            project["id"],
            ProjectEmployeeAddRequest(employeeId=employee["id"], roleOnProject="Lead"),
        )

        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title="Design dashboard",
                goal="Draft the Work dashboard.",
                leadEmployeeId=employee["id"],
            ),
        )
        events = self.service.list_events("user_1", mission["id"])

        self.assertEqual(employee["name"], "Mira")
        self.assertEqual(mission["leadEmployeeId"], employee["id"])
        self.assertEqual(mission["leadEmployeeName"], "Mira")
        self.assertEqual(mission["leadEmployeeRole"], "Product Designer")
        self.assertEqual(events[0]["payload"]["employee"]["name"], "Mira")
        self.assertEqual(events[0]["payload"]["employee"]["role"], "Product Designer")

    def test_user_agent_can_lead_mission_without_project_team(self) -> None:
        project = self.service.create_project(
            "user_1",
            ProjectCreateRequest(name="Novel"),
        )

        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title="Outline",
                goal="Plan an 8000 word novel.",
                leadEmployeeId="agent_1",
            ),
            [
                {
                    "slot": "agent_1",
                    "name": "Plotter",
                    "voice": "precise outline lead",
                    "personality": "Plans carefully.",
                    "story": "Knows serialized fiction.",
                },
                {
                    "slot": "agent_2",
                    "name": "Drafter",
                    "voice": "fast prose writer",
                    "personality": "Drafts quickly.",
                    "story": "",
                },
            ],
        )
        events = self.service.list_events("user_1", mission["id"])

        self.assertEqual(mission["leadEmployeeId"], "agent_1")
        self.assertEqual(mission["leadEmployeeName"], "Plotter")
        self.assertEqual(mission["leadEmployeeRole"], "precise outline lead")
        self.assertEqual(events[0]["payload"]["employee"]["id"], "agent_1")
        self.assertEqual(events[0]["payload"]["employee"]["name"], "Plotter")

    def test_employee_must_join_project_before_leading_mission(self) -> None:
        project = self.service.create_project(
            "user_1",
            ProjectCreateRequest(name="Cyber1924"),
        )
        employee = self.service.create_employee(
            "user_1",
            EmployeeCreateRequest(name="Naomi", role="Reviewer"),
        )

        with self.assertRaises(HTTPException) as error:
            self.service.create_mission(
                "user_1",
                MissionCreateRequest(
                    projectId=project["id"],
                    title="Review",
                    goal="Review the UI.",
                    leadEmployeeId=employee["id"],
                ),
            )

        self.assertEqual(error.exception.status_code, 422)

    def test_start_rejects_double_start(self) -> None:
        mission = self._mission()

        self.service.start_mission("user_1", mission["id"], MissionStartRequest())

        with self.assertRaises(HTTPException):
            self.service.start_mission("user_1", mission["id"], MissionStartRequest())

    def test_worker_completes_v0_event_sequence(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]

        MissionWorker(self.service, runner=FakeMissionRunner("Generated result.")).run_v0_mission(
            "user_1",
            mission["id"],
            run_id,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in completed["events"]]
        self.assertEqual(completed["mission"]["status"], "completed")
        self.assertIn("RAW_LOG", event_types)
        self.assertIn("PRODUCT_UPDATED", event_types)
        self.assertEqual(event_types[-1], "MISSION_COMPLETED")

    def test_worker_persists_text_artifact_from_runner(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]

        MissionWorker(self.service, runner=FakeMissionRunner("Chapter 1\nA real draft exists.")).run_v0_mission(
            "user_1",
            mission["id"],
            run_id,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        product_events = [event for event in completed["events"] if event["type"] == "PRODUCT_UPDATED"]

        self.assertEqual(completed["mission"]["status"], "completed")
        self.assertEqual(len(completed["artifacts"]), 1)
        self.assertEqual(completed["artifacts"][0]["kind"], "text")
        self.assertIn("A real draft exists.", completed["artifacts"][0]["content"])
        self.assertEqual(product_events[-1]["payload"]["artifactId"], completed["artifacts"][0]["id"])
        self.assertNotIn("content", product_events[-1]["payload"])
        self.assertIn("Chapter 1", product_events[-1]["payload"]["summary"])

    def test_service_creates_product_and_artifact_lineage_in_mission_detail(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]

        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="8000字小说",
            summary="长篇小说产品。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind="outline",
            title="故事大纲",
            content="一名年轻人追查旧车票背后的秘密。",
            summary="完成故事大纲。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
            source_artifact_ids=[],
            work_window_id=None,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(completed["products"][0]["id"], product["id"])
        self.assertEqual(completed["products"][0]["latestArtifactId"], artifact["id"])
        self.assertEqual(completed["products"][0]["artifactIds"], [artifact["id"]])
        self.assertEqual(completed["artifacts"][0]["metadata"]["productId"], product["id"])
        self.assertEqual(completed["artifacts"][0]["metadata"]["sourceArtifactIds"], [])

    def test_service_tracks_visible_work_window_result(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="8000字小说",
            summary="长篇小说产品。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )

        window = self.service.create_work_window(
            "user_1",
            mission["id"],
            run_id,
            agent_slot="agent_2",
            title="第一章草稿",
            brief="写第一章。",
            metadata={"expectedOutput": "chapter"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind="chapter",
            title="第一章",
            content="雨夜车站。",
            summary="完成第一章。",
            created_by={"id": "agent_2", "name": "Writer", "role": "delegate"},
            source_artifact_ids=[],
            work_window_id=window["id"],
        )
        completed_window = self.service.complete_work_window(
            "user_1",
            window["id"],
            result_artifact_id=artifact["id"],
            summary="第一章草稿完成。",
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(completed_window["status"], "completed")
        self.assertEqual(completed["workWindows"][0]["id"], window["id"])
        self.assertEqual(completed["workWindows"][0]["resultArtifactId"], artifact["id"])
        self.assertEqual(completed["workWindows"][0]["agentSlot"], "agent_2")
        self.assertEqual(completed["artifacts"][0]["metadata"]["workWindowId"], window["id"])

    def test_worker_marks_active_step_failed_when_runner_fails(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]

        MissionWorker(self.service, runner=FailingMissionRunner("model_timeout")).run_v0_mission(
            "user_1",
            mission["id"],
            run_id,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        failed_steps = [step for step in self.repository.steps.values() if step["mission_id"] == mission["id"]]
        failed_events = [event for event in completed["events"] if event["type"] == "MISSION_FAILED"]

        self.assertEqual(completed["mission"]["status"], "failed")
        self.assertEqual(completed["mission"]["lastError"], "model_timeout")
        self.assertEqual(completed["latestRun"]["status"], "failed")
        self.assertEqual(failed_steps[0]["status"], "failed")
        self.assertEqual(failed_events[-1]["stepId"], failed_steps[0]["_id"])

    def test_event_pagination_uses_after_sequence(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        MissionWorker(self.service, runner=FakeMissionRunner("Generated result.")).run_v0_mission(
            "user_1",
            mission["id"],
            run_id,
        )

        events = self.service.list_events("user_1", mission["id"], after_sequence=2)

        self.assertTrue(all(event["sequence"] > 2 for event in events))

    def test_worker_stops_when_stop_is_requested_before_next_worker_tick(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]

        stopped_detail = self.service.stop_mission("user_1", mission["id"], MissionStopRequest(reason="Hold"))
        MissionWorker(self.service, runner=FakeMissionRunner("Generated result.")).run_v0_mission(
            "user_1",
            mission["id"],
            run_id,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in completed["events"]]
        self.assertEqual(stopped_detail["mission"]["status"], "stopping")
        self.assertEqual(completed["mission"]["status"], "stopped")
        self.assertEqual(completed["latestRun"]["status"], "stopped")
        self.assertIn("MISSION_STOP_REQUESTED", event_types)
        self.assertEqual(event_types[-1], "MISSION_STOPPED")

    def test_worker_event_delay_env_invalid_value_falls_back_to_zero(self) -> None:
        original = os.environ.get("HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS")
        os.environ["HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS"] = "not-a-number"
        try:
            self.assertEqual(_event_delay_seconds(), 0.0)
        finally:
            if original is None:
                os.environ.pop("HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS", None)
            else:
                os.environ["HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS"] = original

    def test_model_mission_runner_supports_codex_cli_provider(self) -> None:
        codex_client = RecordingModelClient("codex_cli")
        runner = ModelMissionRunner(
            ModelRuntime(
                config_repository=StaticCodexConfigRepository(),
                client=RecordingModelClient("openai_compatible"),
                codex_cli_client=codex_client,
            )
        )
        mission = self._mission()
        project = self.service.get_mission_detail("user_1", mission["id"])["project"]

        result = runner.run(
            {
                "project": project,
                "mission": mission,
                "runId": "run_1",
                "employee": {"id": "agent_1", "name": "Writer", "role": "writes"},
            }
        )

        self.assertEqual(result["content"], "codex work artifact")
        self.assertEqual(result["metadata"]["provider"], "codex_cli")
        self.assertIsNotNone(codex_client.last_request)
        self.assertEqual(codex_client.last_request.max_output_tokens, 1200)
        self.assertEqual(codex_client.last_request.reasoning_effort, "low")
        self.assertIn("bounded V0.5 pass", codex_client.last_request.messages[0].content)
        self.assertIn("600-1200 Chinese characters", codex_client.last_request.messages[1].content)

    def _mission(self) -> dict[str, Any]:
        project = self.service.create_project(
            "user_1",
            ProjectCreateRequest(name="Demo"),
        )
        return self.service.create_mission(
            "user_1",
            MissionCreateRequest(projectId=project["id"], title="Mission", goal="Run V0."),
        )


class FakeMissionRunner:
    def __init__(self, content: str) -> None:
        self.content = content

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "kind": "text",
            "title": context["mission"]["title"],
            "content": self.content,
            "metadata": {"runner": "fake"},
        }


class FailingMissionRunner:
    def __init__(self, error: str) -> None:
        self.error = error

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError(self.error)


class StaticCodexConfigRepository:
    def get_enabled_config(self) -> ModelRuntimeConfig:
        return ModelRuntimeConfig(
            provider="codex_cli",
            base_url="codex-cli",
            model_name="gpt-5.4",
            api_key="codex-cli-auth",
            codex_command="/usr/local/bin/codex",
        )


class RecordingModelClient:
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.last_request: ModelGenerateRequest | None = None

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse:
        self.last_request = request
        return ModelGenerateResponse(text="codex work artifact", model_name=config.model_name, provider=config.provider)
