"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database


class MemoryRepository:
    """MongoDB persistence for evidence-backed memory cards."""

    def __init__(self, database: Database):
        self.memory_cards: Collection = database["memory_cards"]

    def ensure_indexes(self) -> None:
        self.memory_cards.create_index(
            [
                ("user_id", ASCENDING),
                ("scope", ASCENDING),
                ("owner_type", ASCENDING),
                ("owner_id", ASCENDING),
                ("memory_type", ASCENDING),
                ("updated_at", DESCENDING),
            ]
        )
        self.memory_cards.create_index(
            [("user_id", ASCENDING), ("status", ASCENDING), ("importance_score", DESCENDING), ("updated_at", DESCENDING)]
        )
        self.memory_cards.create_index([("user_id", ASCENDING), ("source_message_ids", ASCENDING)])
        self.memory_cards.create_index([("user_id", ASCENDING), ("dedupe_hash", ASCENDING)], unique=True)

    def upsert_memory_card(self, document: dict[str, Any]) -> dict[str, Any]:
        set_document = dict(document)
        created_at = set_document.pop("created_at")
        result = self.memory_cards.find_one_and_update(
            {"user_id": document["user_id"], "dedupe_hash": document["dedupe_hash"]},
            {"$set": set_document, "$setOnInsert": {"created_at": created_at}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert result is not None
        return result

    def list_memory_cards(
        self,
        user_id: str,
        scope: str,
        owner_type: str | None,
        owner_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id, "scope": scope, "status": "active"}
        if owner_type is not None:
            query["owner_type"] = owner_type
        if owner_id is not None:
            query["owner_id"] = owner_id
        return list(
            self.memory_cards.find(query)
            .sort([("importance_score", DESCENDING), ("updated_at", DESCENDING)])
            .limit(limit)
        )
