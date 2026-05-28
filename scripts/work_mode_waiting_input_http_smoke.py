"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from users.auth import get_current_user_id
from work_mode.loop import MissionLoopRunner
from work_mode.routes import get_user_service, get_work_mode_service, get_work_mode_worker_launcher, router
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_routes import FakeUserService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from scripts.work_mode_v1_smoke_helpers import WaitingInputLeadClient

SMOKE_USER_ID = "work_mode_waiting_input_smoke_user"


def main() -> None:
    service = WorkModeService(FakeWorkModeRepository())
    action_client = WaitingInputLeadClient()
    client = _client(service, action_client)

    project = _expect_ok(client.post("/api/work/projects", json={"name": "Waiting Input Smoke"}), 201)
    mission = _expect_ok(
        client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "需要确认方向的小说",
                "goal": "先询问用户是否按受其特质启发的方向开始，再继续写作。",
                "leadEmployeeId": "agent_1",
            },
        ),
        201,
    )

    _expect_ok(client.post(f"/api/work/missions/{mission['id']}/start", json={}), 200)
    waiting = _expect_ok(client.get(f"/api/work/missions/{mission['id']}"), 200)
    assert waiting["mission"]["status"] == "waiting_input", waiting["mission"]
    assert waiting["events"][-1]["type"] == "USER_INPUT_REQUESTED", waiting["events"][-1]

    answered = _expect_ok(
        client.post(f"/api/work/missions/{mission['id']}/answer", json={"answer": "按这个方向开始。"}),
        200,
    )
    assert answered["mission"]["status"] == "running", answered["mission"]
    completed = _expect_ok(client.get(f"/api/work/missions/{mission['id']}"), 200)
    event_types = [event["type"] for event in completed["events"]]
    assert completed["mission"]["status"] == "completed", completed["mission"]
    assert "USER_INPUT_RECEIVED" in event_types, event_types
    assert event_types[-1] == "MISSION_COMPLETED", event_types
    assert completed["products"], completed
    assert action_client.calls >= 3, action_client.calls
    print(
        "work_mode_waiting_input_http_smoke=ok "
        f"events={len(completed['events'])} "
        f"products={len(completed['products'])} "
        f"artifacts={len(completed['artifacts'])}"
    )


def _client(service: WorkModeService, action_client: WaitingInputLeadClient) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/work")
    app.dependency_overrides[get_current_user_id] = lambda: SMOKE_USER_ID
    app.dependency_overrides[get_work_mode_service] = lambda: service
    app.dependency_overrides[get_user_service] = lambda: FakeUserService()
    app.dependency_overrides[get_work_mode_worker_launcher] = lambda: SmokeWorker(service, action_client)
    return TestClient(app)


class SmokeWorker:
    def __init__(self, service: WorkModeService, action_client: WaitingInputLeadClient) -> None:
        self.service = service
        self.action_client = action_client

    def __call__(self, user_id: str, mission_id: str, run_id: str) -> None:
        MissionLoopRunner(self.service, self.action_client, max_turns=6).run(user_id, mission_id, run_id)


def _expect_ok(response, expected_status: int) -> dict | list:
    assert response.status_code == expected_status, response.text
    return response.json()


if __name__ == "__main__":
    main()
