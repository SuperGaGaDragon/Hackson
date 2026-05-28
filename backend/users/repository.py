"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database


class UserRepository:
    """MongoDB persistence boundary for users."""

    def __init__(self, database: Database):
        self.collection: Collection = database["users"]
        self.desktop_handoffs: Collection = database["desktop_auth_handoffs"]

    def ensure_indexes(self) -> None:
        self.collection.create_index([("username_normalized", ASCENDING)], unique=True)
        self.collection.create_index([("email_normalized", ASCENDING)], unique=True)
        self.desktop_handoffs.create_index([("code", ASCENDING)], unique=True)
        self.desktop_handoffs.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)

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

    def bind_desktop_handoff(self, code: str, user_id: str, expires_at: Any) -> dict[str, Any]:
        document = {
            "code": code,
            "user_id": user_id,
            "expires_at": expires_at,
            "claimed_at": None,
        }
        self.desktop_handoffs.update_one({"code": code}, {"$set": document}, upsert=True)
        stored = self.desktop_handoffs.find_one({"code": code})
        assert stored is not None
        return stored

    def claim_desktop_handoff(self, code: str, claimed_at: Any) -> dict[str, Any] | None:
        return self.desktop_handoffs.find_one_and_update(
            {
                "code": code,
                "claimed_at": None,
                "expires_at": {"$gt": claimed_at},
            },
            {"$set": {"claimed_at": claimed_at}},
            return_document=ReturnDocument.AFTER,
        )
