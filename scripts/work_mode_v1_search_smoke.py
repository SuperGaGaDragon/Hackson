"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
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
from scripts.work_mode_v1_smoke_helpers import FakeSearchProvider, SearchSmokeLeadClient, assert_search_acceptance


def main() -> None:
    service = WorkModeService(FakeWorkModeRepository())
    mission = _mission(service)
    detail = service.start_mission("smoke_user", mission["id"], MissionStartRequest())
    run_id = detail["activeRun"]["id"]
    lead_client = SearchSmokeLeadClient()

    MissionLoopRunner(
        service,
        action_client=lead_client,
        executor=WorkModeToolExecutor(service, search_provider=FakeSearchProvider()),
        max_turns=5,
        max_invalid_turns=2,
    ).run("smoke_user", mission["id"], run_id)

    completed = service.get_mission_detail("smoke_user", mission["id"])
    acceptance = assert_search_acceptance(completed, lead_client)
    print(
        "work_mode_v1_search_smoke=ok "
        f"events={len(completed['events'])} "
        f"products={len(completed['products'])} "
        f"artifacts={len(completed['artifacts'])} "
        f"final_artifact={acceptance['finalArtifact']['id']}"
    )


def _mission(service: WorkModeService) -> dict:
    project = service.create_project("smoke_user", ProjectCreateRequest(name="Search Smoke"))
    return service.create_mission(
        "smoke_user",
        MissionCreateRequest(
            projectId=project["id"],
            title="查找资料并写摘要",
            goal="查找一个可引用资料，并写成简短摘要。",
            leadEmployeeId="agent_1",
        ),
        [
            {"slot": "agent_1", "name": "Planner", "voice": "lead", "personality": "Plans.", "story": ""},
            {"slot": "agent_2", "name": "Writer", "voice": "delegate", "personality": "Writes.", "story": ""},
        ],
    )


if __name__ == "__main__":
    main()
