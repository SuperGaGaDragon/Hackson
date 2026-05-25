"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from bson import ObjectId
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.database import Database


class UserRepository:
    """MongoDB persistence boundary for users."""

    def __init__(self, database: Database):
        self.collection: Collection = database["users"]

    def ensure_indexes(self) -> None:
        self.collection.create_index([("username_normalized", ASCENDING)], unique=True)
        self.collection.create_index([("email_normalized", ASCENDING)], unique=True)

    def create(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.collection.insert_one(document)
        created = self.collection.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        return self.collection.find_one({"_id": ObjectId(user_id)})

    def find_by_identifier(self, identifier: str) -> dict[str, Any] | None:
        normalized = identifier.strip().lower()
        return self.collection.find_one(
            {
                "$or": [
                    {"username_normalized": normalized},
                    {"email_normalized": normalized},
                ]
            }
        )

    def update(self, user_id: str, changes: dict[str, Any]) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id):
            return None
        self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": changes})
        return self.collection.find_one({"_id": ObjectId(user_id)})
