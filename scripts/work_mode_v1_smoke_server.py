"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from __future__ import annotations

from pathlib import Path

import sys
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from conversations.model import now_utc
from users.auth import get_current_user_id
from users.auth import get_user_service
from users.model import public_user
from users.routes import router as users_router
from work_mode.loop import MissionLoopRunner
from work_mode.routes import get_user_service as get_work_user_service
from work_mode.routes import get_work_mode_service, get_work_mode_worker_launcher
from work_mode.routes import router as work_router
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from scripts.work_mode_v1_smoke_helpers import FullSmokeDelegateClient, FullSmokeLeadClient

def create_smoke_app() -> FastAPI:
    """Create an isolated HTTP app for Work Mode browser smoke."""
    work_service = WorkModeService(FakeWorkModeRepository())
    user_service = SmokeAuthUserService()
    app = FastAPI(title="Hackson Work Mode V1 Smoke")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(users_router, prefix="/api/users", tags=["users"])
    app.include_router(work_router, prefix="/api/work", tags=["work-mode"])
    app.dependency_overrides[get_current_user_id] = lambda: "smoke_user"
    app.dependency_overrides[get_user_service] = lambda: user_service
    app.dependency_overrides[get_work_user_service] = lambda: user_service
    app.dependency_overrides[get_work_mode_service] = lambda: work_service
    app.dependency_overrides[get_work_mode_worker_launcher] = lambda: SmokeWorker(work_service)

    @app.get("/api/agents")
    def list_agents() -> list[dict[str, Any]]:
        return SmokeAgentService().list_agents()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


class SmokeAuthUserService:
    """Minimal in-memory user service for authenticated browser smoke."""

    def __init__(self) -> None:
        self.user = _smoke_user()

    def register(self, payload) -> dict[str, Any]:
        return self._auth_response()

    def login(self, payload) -> dict[str, Any]:
        return self._auth_response()

    def get_user(self, user_id: str) -> dict[str, Any]:
        return public_user(self.user)

    def update_user(self, user_id: str, payload) -> dict[str, Any]:
        return public_user(self.user)

    def _auth_response(self) -> dict[str, Any]:
        return {"accessToken": "smoke-token", "tokenType": "bearer", "user": public_user(self.user)}


class SmokeAgentService:
    def list_agents(self) -> list[dict[str, Any]]:
        return public_user(_smoke_user())["agentProfiles"]


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


def _smoke_user() -> dict[str, Any]:
    timestamp = now_utc()
    return {
        "_id": "smoke_user",
        "username": "worksmoke",
        "display_name": "Work Smoke",
        "email": "worksmoke@example.com",
        "idle_on": True,
        "language_preference": "zh",
        "personality": "",
        "story": "",
        "agent_profiles": [
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
        "created_at": timestamp,
        "updated_at": timestamp,
    }


app = create_smoke_app()
