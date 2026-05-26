"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database


class DiaryRepository:
    """MongoDB persistence for Agent diary entries."""

    def __init__(self, database: Database):
        self.diary_entries: Collection = database["diary_entries"]

    def ensure_indexes(self) -> None:
        self.diary_entries.create_index([("user_id", ASCENDING), ("agent_id", ASCENDING), ("created_at", DESCENDING)])
        self.diary_entries.create_index([("user_id", ASCENDING), ("source_message_ids", ASCENDING)])

    def create_diary_entry(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.diary_entries.insert_one(document)
        created = self.diary_entries.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def list_diary_entries(self, user_id: str, agent_id: str | None, limit: int) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if agent_id is not None:
            query["agent_id"] = agent_id
        return list(self.diary_entries.find(query).sort("created_at", DESCENDING).limit(limit))
