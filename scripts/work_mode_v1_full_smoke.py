"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from __future__ import annotations

from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from work_mode.loop import MissionLoopRunner
from work_mode.schemas import MissionCreateRequest, MissionStartRequest, ProjectCreateRequest
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from scripts.work_mode_v1_smoke_helpers import (
    FullSmokeDelegateClient,
    FullSmokeLeadClient,
    assert_full_acceptance,
    cjk_count,
    final_artifact_from_detail,
)


def main() -> None:
    service = WorkModeService(FakeWorkModeRepository())
    mission = _mission(service)
    detail = service.start_mission("smoke_user", mission["id"], MissionStartRequest())
    run_id = detail["activeRun"]["id"]
    lead_client = FullSmokeLeadClient()
    delegate_client = FullSmokeDelegateClient()

    MissionLoopRunner(
        service,
        action_client=lead_client,
        executor=WorkModeToolExecutor(service, delegate_client=delegate_client),
        max_turns=12,
        max_invalid_turns=2,
    ).run("smoke_user", mission["id"], run_id)

    completed = service.get_mission_detail("smoke_user", mission["id"])
    acceptance = assert_full_acceptance(completed)
    final_artifact = acceptance["finalArtifact"]
    print(
        "work_mode_v1_full_smoke=ok "
        f"events={len(completed['events'])} "
        f"windows={len(completed['workWindows'])} "
        f"products={len(completed['products'])} "
        f"artifacts={len(completed['artifacts'])} "
        f"final_cjk={cjk_count(final_artifact['content'])}"
    )


def _mission(service: WorkModeService) -> dict:
    project = service.create_project("smoke_user", ProjectCreateRequest(name="Novel Smoke"))
    return service.create_mission(
        "smoke_user",
        MissionCreateRequest(
            projectId=project["id"],
            title="写一个8000字小说",
            goal="写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。",
            leadEmployeeId="agent_1",
        ),
        [
            {"slot": "agent_1", "name": "Planner", "voice": "lead", "personality": "Plans.", "story": ""},
            {"slot": "agent_2", "name": "Writer", "voice": "delegate", "personality": "Writes.", "story": ""},
        ],
    )


def _final_artifact(detail: dict) -> dict:
    return final_artifact_from_detail(detail)


if __name__ == "__main__":
    main()
