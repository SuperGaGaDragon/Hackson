"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database


class ContextPackageRepository:
    """MongoDB persistence boundary for auditable context package records."""

    def __init__(self, database: Database):
        self.collection: Collection = database["context_packages"]

    def ensure_indexes(self) -> None:
        self.collection.create_index([("user_id", ASCENDING), ("conversation_id", ASCENDING), ("created_at", DESCENDING)])
        self.collection.create_index([("user_id", ASCENDING), ("prompt_hash", ASCENDING)])
        self.collection.create_index([("user_id", ASCENDING), ("full_prompt_text_expires_at", ASCENDING)])

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.collection.insert_one(document)
        created = self.collection.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def list_prompt_logs(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return list(
            self.collection.find(
                {
                    "user_id": user_id,
                    "full_prompt_text": {"$ne": None},
                }
            )
            .sort("created_at", DESCENDING)
            .limit(limit)
        )

    def clear_prompt_text(self, user_id: str, timestamp) -> int:
        result = self.collection.update_many(
            {
                "user_id": user_id,
                "full_prompt_text": {"$ne": None},
            },
            {
                "$set": {
                    "full_prompt_text": None,
                    "full_prompt_text_deleted_at": timestamp,
                    "full_prompt_text_expires_at": None,
                    "updated_at": timestamp,
                }
            },
        )
        return int(result.modified_count)

    def clear_expired_prompt_text(self, timestamp) -> int:
        result = self.collection.update_many(
            {
                "full_prompt_text": {"$ne": None},
                "full_prompt_text_expires_at": {"$lte": timestamp},
            },
            {
                "$set": {
                    "full_prompt_text": None,
                    "full_prompt_text_deleted_at": timestamp,
                    "updated_at": timestamp,
                }
            },
        )
        return int(result.modified_count)
