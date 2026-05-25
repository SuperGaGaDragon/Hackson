"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database


class ConversationRepository:
    """MongoDB persistence boundary for conversations and messages."""

    def __init__(self, database: Database):
        self.conversations: Collection = database["conversations"]
        self.messages: Collection = database["messages"]
        self.counters: Collection = database["conversation_counters"]

    def ensure_indexes(self) -> None:
        self.conversations.create_index(
            [("user_id", ASCENDING), ("mode", ASCENDING), ("status", ASCENDING), ("updated_at", DESCENDING)]
        )
        self.conversations.create_index(
            [("user_id", ASCENDING), ("mode", ASCENDING), ("last_message_at", DESCENDING)]
        )
        self.conversations.create_index([("parent_conversation_id", ASCENDING)])
        self.messages.create_index([("conversation_id", ASCENDING), ("sequence", ASCENDING)], unique=True)
        self.messages.create_index([("conversation_id", ASCENDING), ("created_at", DESCENDING)])
        self.messages.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
        self.messages.create_index(
            [("user_id", ASCENDING), ("sender_slot", ASCENDING), ("created_at", DESCENDING)]
        )
        self.counters.create_index([("conversation_id", ASCENDING)], unique=True)

    def create_conversation(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.conversations.insert_one(document)
        self.counters.insert_one({"conversation_id": result.inserted_id, "sequence": 0})
        created = self.conversations.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_conversation(self, conversation_id: str, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(conversation_id):
            return None
        return self.conversations.find_one({"_id": ObjectId(conversation_id), "user_id": user_id})

    def list_conversations(
        self,
        user_id: str,
        mode: str | None,
        status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {"user_id": user_id}
        if mode is not None:
            query["mode"] = mode
        if status is not None:
            query["status"] = status
        return list(
            self.conversations.find(query)
            .sort([("last_message_at", DESCENDING), ("updated_at", DESCENDING)])
            .limit(limit)
        )

    def find_active_idle_conversation(self, user_id: str) -> dict[str, Any] | None:
        return self.conversations.find_one(
            {"user_id": user_id, "mode": "idle", "status": "active"},
            sort=[("updated_at", DESCENDING)],
        )

    def next_sequence(self, conversation_object_id: ObjectId) -> int:
        counter = self.counters.find_one_and_update(
            {"conversation_id": conversation_object_id},
            {"$inc": {"sequence": 1}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        assert counter is not None
        return int(counter["sequence"])

    def append_message(
        self,
        conversation: dict[str, Any],
        message: dict[str, Any],
    ) -> dict[str, Any]:
        sequence = self.next_sequence(conversation["_id"])
        message["sequence"] = sequence
        result = self.messages.insert_one(message)
        self.conversations.update_one(
            {"_id": conversation["_id"]},
            {
                "$set": {
                    "updated_at": message["created_at"],
                    "last_message_at": message["created_at"],
                },
                "$inc": {"message_count": 1},
            },
        )
        created = self.messages.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def list_messages(
        self,
        conversation_id: str,
        user_id: str,
        after_sequence: int | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        if not ObjectId.is_valid(conversation_id):
            return []
        query: dict[str, Any] = {
            "conversation_id": ObjectId(conversation_id),
            "user_id": user_id,
        }
        if after_sequence is not None:
            query["sequence"] = {"$gt": after_sequence}
        return list(self.messages.find(query).sort("sequence", ASCENDING).limit(limit))
