"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database


class TaskRepository:
    """MongoDB persistence for Work Mode tasks and tool traces."""

    def __init__(self, database: Database):
        self.tasks: Collection = database["tasks"]
        self.tool_traces: Collection = database["tool_traces"]

    def ensure_indexes(self) -> None:
        self.tasks.create_index([("user_id", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)])
        self.tasks.create_index([("conversation_id", ASCENDING)], unique=True)
        self.tool_traces.create_index([("user_id", ASCENDING), ("task_id", ASCENDING), ("created_at", DESCENDING)])

    def create_task(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.tasks.insert_one(document)
        created = self.tasks.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_task(self, task_id: str, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(task_id):
            return None
        return self.tasks.find_one({"_id": ObjectId(task_id), "user_id": user_id})

    def list_tasks(self, user_id: str, limit: int) -> list[dict[str, Any]]:
        return list(self.tasks.find({"user_id": user_id}).sort("updated_at", DESCENDING).limit(limit))

    def create_tool_trace(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.tool_traces.insert_one(document)
        created = self.tool_traces.find_one({"_id": result.inserted_id})
        assert created is not None
        return created
