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


class SummaryRepository:
    """MongoDB persistence for derived conversation summaries."""

    def __init__(self, database: Database):
        self.summaries: Collection = database["summaries"]

    def ensure_indexes(self) -> None:
        self.summaries.create_index(
            [("user_id", ASCENDING), ("conversation_id", ASCENDING), ("summary_type", ASCENDING), ("updated_at", DESCENDING)]
        )
        self.summaries.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])

    def create_summary(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.summaries.insert_one(document)
        created = self.summaries.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def get_latest_summary(
        self,
        user_id: str,
        conversation_id: str,
        summary_type: str,
    ) -> dict[str, Any] | None:
        return self.summaries.find_one(
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "summary_type": summary_type,
            },
            sort=[("updated_at", DESCENDING)],
        )
