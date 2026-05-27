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
from work_mode.routes import get_work_mode_service, get_work_mode_worker_launcher, router
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository

TEST_USER_ID = "work_route_user"


class WorkModeRoutesTest(TestCase):
    def setUp(self) -> None:
        self.service = WorkModeService(FakeWorkModeRepository())
        app = FastAPI()
        app.include_router(router, prefix="/api/work")
        app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
        app.dependency_overrides[get_work_mode_service] = lambda: self.service
        app.dependency_overrides[get_work_mode_worker_launcher] = lambda: lambda user_id, mission_id, run_id: None
        self.client = TestClient(app)

    def test_project_mission_start_and_events_routes(self) -> None:
        project_response = self.client.post(
            "/api/work/projects",
            json={"name": "Cyber1924", "repoPath": "/repos/cyber1924"},
        )
        self.assertEqual(project_response.status_code, 201)
        project = project_response.json()

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
        self.assertEqual(event_types, ["MISSION_CREATED", "MISSION_STARTED"])

    def test_stop_route_requires_running_mission(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo", "repoPath": "/repos/demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run V0."},
        ).json()

        response = self.client.post(f"/api/work/missions/{mission['id']}/stop", json={"reason": "pause"})

        self.assertEqual(response.status_code, 409)

    def test_stop_route_records_stop_requested_for_running_mission(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo", "repoPath": "/repos/demo"}).json()
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
