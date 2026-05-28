"""
Created at: 2026-05-27
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
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from scripts.work_mode_v1_smoke_helpers import (
    FullSmokeDelegateClient,
    FullSmokeLeadClient,
    assert_full_acceptance,
)

SMOKE_USER_ID = "work_mode_http_smoke_user"


def main() -> None:
    service = WorkModeService(FakeWorkModeRepository())
    client = _client(service)

    project = _expect_ok(client.post("/api/work/projects", json={"name": "Novel HTTP Smoke"}), 201)
    mission = _expect_ok(
        client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "写一个8000字小说",
                "goal": "写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。",
                "leadEmployeeId": "agent_1",
            },
        ),
        201,
    )
    _expect_ok(client.post(f"/api/work/missions/{mission['id']}/start", json={}), 200)
    detail = _expect_ok(client.get(f"/api/work/missions/{mission['id']}"), 200)
    acceptance = assert_full_acceptance(detail)
    evaluation = _expect_ok(client.post(f"/api/work/missions/{mission['id']}/evaluate", json={}), 200)
    report_artifact = _expect_report_artifact(evaluation)
    report_payload = report_artifact["metadata"]["reportPayload"]
    events = _expect_ok(client.get(f"/api/work/missions/{mission['id']}/events"), 200)
    assert any(event["type"] == "RELIABILITY_REPORTED" for event in events), "missing_reliability_reported_event"

    print(
        "work_mode_v1_http_smoke=ok "
        f"events={len(events)} "
        f"windows={len(detail['workWindows'])} "
        f"products={len(detail['products'])} "
        f"artifacts={len(detail['artifacts'])} "
        f"reliability_score={report_payload['score']} "
        f"reliability_status={report_payload['status']} "
        f"final_cjk={acceptance['finalCjk']}"
    )


def _client(service: WorkModeService) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/work")
    app.dependency_overrides[get_current_user_id] = lambda: SMOKE_USER_ID
    app.dependency_overrides[get_work_mode_service] = lambda: service
    app.dependency_overrides[get_user_service] = lambda: SmokeUserService()
    app.dependency_overrides[get_work_mode_worker_launcher] = lambda: SmokeWorker(service)
    return TestClient(app)


class SmokeUserService:
    def get_user(self, user_id: str) -> dict:
        return {
            "id": user_id,
            "agentProfiles": [
                {
                    "slot": "agent_1",
                    "name": "Planner",
                    "short": "A1",
                    "color": "teal",
                    "voice": "lead",
                    "personality": "Plans long writing missions.",
                    "story": "",
                },
                {
                    "slot": "agent_2",
                    "name": "Writer",
                    "short": "A2",
                    "color": "amber",
                    "voice": "delegate",
                    "personality": "Writes chapter drafts.",
                    "story": "",
                },
            ],
        }


class SmokeWorker:
    def __init__(self, service: WorkModeService) -> None:
        self.service = service

    def __call__(self, user_id: str, mission_id: str, run_id: str) -> None:
        MissionLoopRunner(
            self.service,
            action_client=FullSmokeLeadClient(),
            executor=WorkModeToolExecutor(self.service, delegate_client=FullSmokeDelegateClient()),
            max_turns=12,
            max_invalid_turns=2,
        ).run(user_id, mission_id, run_id)


def _expect_ok(response, expected_status: int) -> dict | list:
    assert response.status_code == expected_status, response.text
    return response.json()


def _expect_report_artifact(detail: dict) -> dict:
    reports = [
        artifact
        for artifact in detail["artifacts"]
        if artifact.get("metadata", {}).get("artifactRole") == "reliability_report"
    ]
    assert reports, "missing_reliability_report_artifact"
    report = reports[0]
    payload = report["metadata"].get("reportPayload")
    assert isinstance(payload, dict), "missing_reliability_report_payload"
    assert isinstance(payload.get("score"), int), "missing_reliability_score"
    assert payload.get("profile") == "research_reliability_v1", "unexpected_reliability_profile"
    return report


if __name__ == "__main__":
    main()
