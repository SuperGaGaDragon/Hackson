"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from memory.routes import get_memory_service, router
from users.auth import get_current_user_id


class FakeMemoryService:
    def __init__(self) -> None:
        self.listed_for: tuple[str, bool, int] | None = None
        self.updated: tuple[str, str, str] | None = None
        self.deleted: tuple[str, str] | None = None

    def list_user_memory(self, user_id: str, *, include_deleted: bool = False, limit: int = 50) -> dict:
        self.listed_for = (user_id, include_deleted, limit)
        return {
            "memoryCards": [
                {
                    "id": "memory_1",
                    "userId": user_id,
                    "scope": "companion",
                    "ownerType": "user",
                    "ownerId": user_id,
                    "memoryType": "preference",
                    "summary": "User prefers concise replies.",
                    "sourceMessageIds": ["message_1"],
                    "importanceScore": 0.8,
                    "confidence": 0.9,
                    "status": "active",
                    "metadata": {},
                    "createdAt": "2026-05-28T00:00:00Z",
                    "updatedAt": "2026-05-28T00:00:00Z",
                }
            ]
        }

    def update_status(self, user_id: str, memory_id: str, status_value: str) -> dict:
        self.updated = (user_id, memory_id, status_value)
        card = self.list_user_memory(user_id)["memoryCards"][0]
        card["status"] = status_value
        return card

    def delete_memory(self, user_id: str, memory_id: str) -> dict:
        self.deleted = (user_id, memory_id)
        return {"deletedMemoryCard": True}


class MemoryRoutesTest(TestCase):
    def setUp(self) -> None:
        self.memory_service = FakeMemoryService()
        app = FastAPI()
        app.include_router(router, prefix="/api/memory")
        app.dependency_overrides[get_current_user_id] = lambda: "user_1"
        app.dependency_overrides[get_memory_service] = lambda: self.memory_service
        self.client = TestClient(app)

    def test_lists_user_memory(self) -> None:
        response = self.client.get("/api/memory/me?limit=10")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["memoryCards"][0]["summary"], "User prefers concise replies.")
        self.assertEqual(self.memory_service.listed_for, ("user_1", False, 10))

    def test_user_can_disable_memory(self) -> None:
        response = self.client.patch("/api/memory/me/memory_1", json={"status": "disabled"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "disabled")
        self.assertEqual(self.memory_service.updated, ("user_1", "memory_1", "disabled"))

    def test_user_can_delete_memory(self) -> None:
        response = self.client.delete("/api/memory/me/memory_1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"deletedMemoryCard": True})
        self.assertEqual(self.memory_service.deleted, ("user_1", "memory_1"))
