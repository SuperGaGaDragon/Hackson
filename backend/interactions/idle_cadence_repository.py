"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any

from pymongo import ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database


class IdleRunnerStateRepository:
    """MongoDB persistence boundary for Background Idle runner state."""

    def __init__(self, database: Database):
        self.collection: Collection = database["idle_runner_state"]

    def ensure_indexes(self) -> None:
        self.collection.create_index([("user_id", ASCENDING), ("conversation_id", ASCENDING)], unique=True)

    def get_state(self, user_id: str, conversation_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"user_id": user_id, "conversation_id": conversation_id})

    def upsert_state(self, user_id: str, conversation_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        row = self.collection.find_one_and_update(
            {"user_id": user_id, "conversation_id": conversation_id},
            {
                "$set": {
                    **changes,
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert row is not None
        return row
