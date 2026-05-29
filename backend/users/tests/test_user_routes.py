"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from users.auth import get_current_user_id
from users.routes import get_context_package_service, get_user_service, router


class FakeContextPackageService:
    def __init__(self) -> None:
        self.listed_for: str | None = None
        self.deleted_for: str | None = None

    def list_prompt_logs(self, user_id: str, limit: int = 20) -> dict:
        self.listed_for = user_id
        return {
            "promptLogs": [
                {
                    "id": "context_package_1",
                    "conversationId": "conv_1",
                    "mode": "idle",
                    "targetAgentId": "agent_1",
                    "promptHash": "abc",
                    "tokenEstimate": 42,
                    "createdAt": "2026-05-28T00:00:00Z",
                    "fullPromptTextExpiresAt": "2026-06-27T00:00:00Z",
                    "fullPromptText": "system: prompt",
                }
            ]
        }

    def delete_prompt_logs(self, user_id: str) -> dict:
        self.deleted_for = user_id
        return {"deletedPromptLogs": 1}


class FakeUserService:
    def __init__(self) -> None:
        self.bound: tuple[str, str] | None = None
        self.claimed: str | None = None
        self.quick_source: str | None = None

    def bind_desktop_handoff(self, user_id, payload):
        self.bound = (user_id, payload.code)
        return {"status": "linked"}

    def claim_desktop_handoff(self, payload):
        self.claimed = payload.code
        if payload.code == "desktop-code-linked":
            return {
                "status": "authorized",
                "accessToken": "token_1",
                "tokenType": "bearer",
                "user": {
                    "id": "user_1",
                    "username": "demo",
                    "displayName": "Demo",
                    "email": "demo@example.com",
                    "idleOn": True,
                    "backgroundIdleOn": False,
                    "fullPromptLoggingOn": True,
                    "languagePreference": "en",
                    "personality": "",
                    "story": "",
                    "agentProfiles": [],
                    "isTemporary": False,
                    "createdAt": "2026-05-28T00:00:00Z",
                    "updatedAt": "2026-05-28T00:00:00Z",
                },
            }
        return {"status": "pending"}

    def quick_try(self, payload):
        self.quick_source = payload.source
        return {
            "accessToken": "quick_token",
            "tokenType": "bearer",
            "user": {
                "id": "quick_1",
                "username": "quick_demo",
                "displayName": "Quick Try",
                "email": "quick_demo@quick.hackson.catachess.com",
                "idleOn": True,
                "backgroundIdleOn": False,
                "fullPromptLoggingOn": False,
                "languagePreference": "en",
                "personality": "I am trying Parallex from the TMLS Agentic Hackathon landing page.",
                "story": "",
                "agentProfiles": [],
                "isTemporary": True,
                "createdAt": "2026-05-28T00:00:00Z",
                "updatedAt": "2026-05-28T00:00:00Z",
            },
        }


class UserRoutesTest(TestCase):
    def setUp(self) -> None:
        self.context_service = FakeContextPackageService()
        self.user_service = FakeUserService()
        app = FastAPI()
        app.include_router(router, prefix="/api/users")
        app.dependency_overrides[get_current_user_id] = lambda: "user_1"
        app.dependency_overrides[get_context_package_service] = lambda: self.context_service
        app.dependency_overrides[get_user_service] = lambda: self.user_service
        self.client = TestClient(app)

    def test_me_prompt_logs_are_viewable_but_not_editable(self) -> None:
        response = self.client.get("/api/users/me/prompt-logs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["promptLogs"][0]["fullPromptText"], "system: prompt")
        self.assertEqual(self.context_service.listed_for, "user_1")
        self.assertEqual(self.client.patch("/api/users/me/prompt-logs").status_code, 405)

    def test_me_prompt_logs_delete_clears_retained_prompt_text(self) -> None:
        response = self.client.delete("/api/users/me/prompt-logs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"deletedPromptLogs": 1})
        self.assertEqual(self.context_service.deleted_for, "user_1")

    def test_desktop_handoff_bind_uses_current_user(self) -> None:
        response = self.client.post("/api/users/desktop-handoff", json={"code": "desktop-code-linked"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "linked"})
        self.assertEqual(self.user_service.bound, ("user_1", "desktop-code-linked"))

    def test_desktop_handoff_claim_does_not_require_current_user(self) -> None:
        response = self.client.post("/api/users/desktop-handoff/claim", json={"code": "desktop-code-linked"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "authorized")
        self.assertEqual(response.json()["accessToken"], "token_1")
        self.assertEqual(self.user_service.claimed, "desktop-code-linked")

    def test_desktop_handoff_claim_can_return_pending(self) -> None:
        response = self.client.post("/api/users/desktop-handoff/claim", json={"code": "desktop-code-pending"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "pending", "accessToken": None, "tokenType": None, "user": None})

    def test_quick_try_does_not_require_current_user(self) -> None:
        response = self.client.post("/api/users/quick-try", json={"source": "hackathon"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["accessToken"], "quick_token")
        self.assertEqual(response.json()["user"]["displayName"], "Quick Try")
        self.assertEqual(self.user_service.quick_source, "hackathon")
