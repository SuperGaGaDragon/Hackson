"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from users.auth import get_current_user_id
from work_mode.routes import get_user_service, get_work_mode_service, get_work_mode_worker_launcher, router
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeMissionRunner, FakeWorkModeRepository
from work_mode.worker import MissionWorker

TEST_USER_ID = "work_route_user"


class FakeUserService:
    def get_user(self, user_id: str) -> dict:
        return {
            "id": user_id,
            "agentProfiles": [
                {
                    "slot": "agent_1",
                    "name": "Planner",
                    "short": "A1",
                    "color": "teal",
                    "voice": "careful planner",
                    "personality": "Plans missions before execution.",
                    "story": "",
                },
                {
                    "slot": "agent_2",
                    "name": "Writer",
                    "short": "A2",
                    "color": "amber",
                    "voice": "direct writer",
                    "personality": "Writes concise drafts.",
                    "story": "",
                },
            ],
        }


class WorkModeRoutesTest(TestCase):
    def setUp(self) -> None:
        self.service = WorkModeService(FakeWorkModeRepository())
        app = FastAPI()
        app.include_router(router, prefix="/api/work")
        app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
        app.dependency_overrides[get_work_mode_service] = lambda: self.service
        app.dependency_overrides[get_user_service] = lambda: FakeUserService()
        app.dependency_overrides[get_work_mode_worker_launcher] = lambda: self.run_worker
        self.client = TestClient(app)

    def run_worker(self, user_id: str, mission_id: str, run_id: str) -> None:
        MissionWorker(self.service, runner=FakeMissionRunner("Route generated artifact.")).run_v0_mission(
            user_id,
            mission_id,
            run_id,
        )

    def test_project_mission_start_and_events_routes(self) -> None:
        project_response = self.client.post(
            "/api/work/projects",
            json={"name": "Cyber1924"},
        )
        self.assertEqual(project_response.status_code, 201)
        project = project_response.json()
        self.assertEqual(project["repoPath"], "")

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Fix OAuth",
                "goal": "Fix Google OAuth login.",
            },
        )
        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()

        start_response = self.client.post(f"/api/work/missions/{mission['id']}/start", json={})
        self.assertEqual(start_response.status_code, 200)
        started = start_response.json()
        self.assertEqual(started["mission"]["status"], "running")
        self.assertEqual(started["activeRun"]["status"], "running")

        events_response = self.client.get(f"/api/work/missions/{mission['id']}/events")
        self.assertEqual(events_response.status_code, 200)
        event_types = [event["type"] for event in events_response.json()]
        self.assertIn("MISSION_STARTED", event_types)
        self.assertIn("PRODUCT_UPDATED", event_types)
        self.assertEqual(event_types[-1], "MISSION_COMPLETED")

        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["mission"]["status"], "completed")
        self.assertEqual(len(detail["artifacts"]), 1)
        self.assertIn("Route generated artifact.", detail["artifacts"][0]["content"])

    def test_mission_detail_response_includes_artifacts(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Draft", "goal": "Write one scene."},
        ).json()
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()

        self.assertEqual(detail["artifacts"], [])

    def test_stop_route_requires_running_mission(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run V0."},
        ).json()

        response = self.client.post(f"/api/work/missions/{mission['id']}/stop", json={"reason": "pause"})

        self.assertEqual(response.status_code, 409)

    def test_stop_route_records_stop_requested_for_running_mission(self) -> None:
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: lambda user_id, mission_id, run_id: None
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run V0."},
        ).json()
        self.client.post(f"/api/work/missions/{mission['id']}/start", json={})

        response = self.client.post(f"/api/work/missions/{mission['id']}/stop", json={"reason": "pause"})

        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail["mission"]["status"], "stopping")
        self.assertEqual(detail["activeRun"]["status"], "running")
        self.assertEqual(
            [event["type"] for event in detail["events"]],
            ["MISSION_CREATED", "MISSION_STARTED", "MISSION_STOP_REQUESTED"],
        )

    def test_employee_routes_allow_project_lead_selection(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        employee_response = self.client.post(
            "/api/work/employees",
            json={
                "name": "Mira",
                "role": "Designer",
                "personality": "Calm",
                "experience": ["Dashboards"],
                "skills": ["ux"],
                "permissions": {"can_edit_files": False},
            },
        )
        self.assertEqual(employee_response.status_code, 201)
        employee = employee_response.json()

        add_response = self.client.post(
            f"/api/work/projects/{project['id']}/employees",
            json={"employeeId": employee["id"], "roleOnProject": "Lead"},
        )
        self.assertEqual(add_response.status_code, 201)

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Mission",
                "goal": "Run V0.",
                "leadEmployeeId": employee["id"],
            },
        )

        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()
        self.assertEqual(mission["leadEmployeeName"], "Mira")
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["events"][0]["payload"]["employee"]["name"], "Mira")

    def test_mission_route_accepts_user_agent_lead_without_team_setup(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Outline",
                "goal": "Plan the novel.",
                "leadEmployeeId": "agent_1",
            },
        )

        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()
        self.assertEqual(mission["leadEmployeeId"], "agent_1")
        self.assertEqual(mission["leadEmployeeName"], "Planner")
        self.assertEqual(mission["leadEmployeeRole"], "careful planner")
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["events"][0]["payload"]["employee"]["id"], "agent_1")
        self.assertEqual(detail["events"][0]["payload"]["employee"]["name"], "Planner")
