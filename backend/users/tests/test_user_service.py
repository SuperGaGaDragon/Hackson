"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any
from unittest import TestCase

from users.schemas import DesktopHandoffBindRequest, DesktopHandoffClaimRequest
from users.schemas import UserRegisterRequest, UserUpdateRequest
from users.service import UserService
from agents.catalog import NORA_DEFAULT_STORY, VALE_DEFAULT_STORY


class FakeUserRepository:
    def __init__(self) -> None:
        self.documents: dict[str, dict[str, Any]] = {}
        self.handoffs: dict[str, dict[str, Any]] = {}
        self.indexes_ready = False

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        document = dict(document)
        document["_id"] = "507f1f77bcf86cd799439011"
        self.documents[str(document["_id"])] = document
        return document

    def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        return self.documents.get(user_id)

    def find_by_identifier(self, identifier: str) -> dict[str, Any] | None:
        normalized = identifier.lower()
        return next(
            (
                doc
                for doc in self.documents.values()
                if doc["username_normalized"] == normalized or doc["email_normalized"] == normalized
            ),
            None,
        )

    def update(self, user_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        document = self.documents.get(user_id)
        if document is None:
            return None
        document.update(changes)
        return document

    def bind_desktop_handoff(self, code: str, user_id: str, expires_at: Any) -> dict[str, Any]:
        handoff = {"code": code, "user_id": user_id, "expires_at": expires_at, "claimed_at": None}
        self.handoffs[code] = handoff
        return handoff

    def claim_desktop_handoff(self, code: str, claimed_at: Any) -> dict[str, Any] | None:
        handoff = self.handoffs.get(code)
        if handoff is None or handoff["claimed_at"] is not None or handoff["expires_at"] <= claimed_at:
            return None
        handoff["claimed_at"] = claimed_at
        return handoff


class UserServiceTest(TestCase):
    def test_register_creates_public_user_without_model_config(self) -> None:
        service = UserService(FakeUserRepository())
        response = service.register(
            UserRegisterRequest(
                username="demo_user",
                email="demo@example.com",
                password="password123",
            )
        )

        user = response["user"]
        self.assertEqual(user["username"], "demo_user")
        self.assertEqual(user["email"], "demo@example.com")
        self.assertTrue(user["idleOn"])
        self.assertFalse(user["backgroundIdleOn"])
        self.assertTrue(user["fullPromptLoggingOn"])
        self.assertEqual(user["personality"], "")
        self.assertEqual(user["story"], "")
        self.assertEqual([agent["slot"] for agent in user["agentProfiles"]], ["agent_1", "agent_2"])
        self.assertEqual([agent["name"] for agent in user["agentProfiles"]], ["Nora", "Vale"])
        self.assertEqual(user["agentProfiles"][0]["story"], NORA_DEFAULT_STORY)
        self.assertEqual(user["agentProfiles"][1]["story"], VALE_DEFAULT_STORY)
        self.assertNotIn("password_hash", user)
        self.assertNotIn("endpoint", user)

    def test_update_user_changes_demo_settings(self) -> None:
        service = UserService(FakeUserRepository())
        registered = service.register(
            UserRegisterRequest(
                username="demo_user",
                email="demo@example.com",
                password="password123",
            )
        )

        updated = service.update_user(
            registered["user"]["id"],
            UserUpdateRequest(
                display_name="Demo",
                idle_on=False,
                background_idle_on=True,
                full_prompt_logging_on=False,
                language_preference="en",
                personality="quiet, direct, product-minded",
                story="I am building a demo and want concise practical help.",
                agentProfiles=[
                    {
                        "slot": "agent_1",
                        "name": "Mira",
                        "voice": "soft skeptic",
                        "personality": "A careful skeptic who notices missing assumptions.",
                        "story": "Grew from Nora but now tracks product risk.",
                    },
                    {
                        "slot": "agent_2",
                        "name": "Rook",
                        "voice": "direct builder",
                        "personality": "A builder who turns vague ideas into shipped steps.",
                        "story": "",
                    },
                ],
            ),
        )

        self.assertEqual(updated["displayName"], "Demo")
        self.assertFalse(updated["idleOn"])
        self.assertTrue(updated["backgroundIdleOn"])
        self.assertFalse(updated["fullPromptLoggingOn"])
        self.assertEqual(updated["languagePreference"], "en")
        self.assertEqual(updated["personality"], "quiet, direct, product-minded")
        self.assertEqual(updated["story"], "I am building a demo and want concise practical help.")
        self.assertEqual(updated["agentProfiles"][0]["name"], "Mira")
        self.assertEqual(updated["agentProfiles"][0]["short"], "A1")
        self.assertEqual(updated["agentProfiles"][0]["color"], "teal")
        self.assertEqual(updated["agentProfiles"][0]["personality"], "A careful skeptic who notices missing assumptions.")
        self.assertEqual(updated["agentProfiles"][1]["name"], "Rook")

    def test_desktop_handoff_claim_is_pending_until_browser_binds_code(self) -> None:
        service = UserService(FakeUserRepository())

        response = service.claim_desktop_handoff(DesktopHandoffClaimRequest(code="desktop-code-123456"))

        self.assertEqual(response, {"status": "pending"})

    def test_desktop_handoff_claim_returns_token_once(self) -> None:
        repository = FakeUserRepository()
        service = UserService(repository)
        registered = service.register(
            UserRegisterRequest(
                username="desktop_user",
                email="desktop@example.com",
                password="password123",
            )
        )
        code = "desktop-code-abcdef"

        self.assertEqual(
            service.bind_desktop_handoff(
                registered["user"]["id"],
                DesktopHandoffBindRequest(code=code),
            ),
            {"status": "linked"},
        )
        first_claim = service.claim_desktop_handoff(DesktopHandoffClaimRequest(code=code))
        second_claim = service.claim_desktop_handoff(DesktopHandoffClaimRequest(code=code))

        self.assertEqual(first_claim["status"], "authorized")
        self.assertEqual(first_claim["user"]["username"], "desktop_user")
        self.assertTrue(first_claim["accessToken"])
        self.assertEqual(second_claim, {"status": "pending"})
