"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Protocol
from uuid import uuid4

from pymongo import ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError


LOCK_TTL_SECONDS = 120


class IdleTurnLockRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def acquire(self, document: dict[str, Any]) -> tuple[bool, dict[str, Any]]: ...
    def complete(self, lock_id: Any, response: dict[str, Any], timestamp: datetime) -> dict[str, Any]: ...
    def fail(self, lock_id: Any, error_detail: str, timestamp: datetime) -> dict[str, Any]: ...


class IdleTurnLockRepository:
    """MongoDB repository for per-transcript idle tick locks."""

    def __init__(self, database: Database):
        self.collection: Collection = database["idle_turn_locks"]

    def ensure_indexes(self) -> None:
        self.collection.create_index(
            [("user_id", ASCENDING), ("conversation_id", ASCENDING), ("message_count", ASCENDING)],
            unique=True,
        )
        self.collection.create_index([("user_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True)
        self.collection.create_index([("expires_at", ASCENDING)])

    def acquire(self, document: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        self._expire_stale(document["created_at"])
        try:
            result = self.collection.insert_one(document)
            created = self.collection.find_one({"_id": result.inserted_id})
            assert created is not None
            return True, created
        except DuplicateKeyError:
            existing = self.collection.find_one(
                {
                    "user_id": document["user_id"],
                    "idempotency_key": document["idempotency_key"],
                }
            )
            if existing is not None:
                if existing.get("status") == "failed":
                    return True, self._revive(existing["_id"], document)
                return False, existing
            existing = self.collection.find_one(
                {
                    "user_id": document["user_id"],
                    "conversation_id": document["conversation_id"],
                    "message_count": document["message_count"],
                }
            )
            assert existing is not None
            if existing.get("status") == "failed":
                return True, self._revive(existing["_id"], document)
            return False, existing

    def complete(self, lock_id: Any, response: dict[str, Any], timestamp: datetime) -> dict[str, Any]:
        self.collection.update_one(
            {"_id": lock_id},
            {"$set": {"status": "completed", "response": response, "updated_at": timestamp}},
        )
        row = self.collection.find_one({"_id": lock_id})
        assert row is not None
        return row

    def fail(self, lock_id: Any, error_detail: str, timestamp: datetime) -> dict[str, Any]:
        self.collection.update_one(
            {"_id": lock_id},
            {"$set": {"status": "failed", "error_detail": error_detail, "updated_at": timestamp}},
        )
        row = self.collection.find_one({"_id": lock_id})
        assert row is not None
        return row

    def _revive(self, lock_id: Any, document: dict[str, Any]) -> dict[str, Any]:
        replacement = {key: value for key, value in document.items() if key != "_id"}
        revived = self.collection.find_one_and_update(
            {"_id": lock_id},
            {
                "$set": replacement,
                "$unset": {"response": "", "error_detail": ""},
            },
            return_document=ReturnDocument.AFTER,
        )
        assert revived is not None
        return revived

    def _expire_stale(self, timestamp: datetime) -> None:
        self.collection.update_many(
            {"status": "running", "expires_at": {"$lte": timestamp}},
            {"$set": {"status": "failed", "error_detail": "idle_turn_lock_expired", "updated_at": timestamp}},
        )


class IdleTurnLockService:
    """Acquire, complete, and fail idle tick idempotency locks."""

    def __init__(self, repository: IdleTurnLockRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def acquire(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_count: int,
        idempotency_key: str | None,
    ) -> tuple[bool, dict[str, Any]]:
        timestamp = now_utc()
        key = idempotency_key or f"generated-{uuid4()}"
        return self.repository.acquire(
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_count": message_count,
                "idempotency_key": key,
                "status": "running",
                "created_at": timestamp,
                "updated_at": timestamp,
                "expires_at": timestamp + timedelta(seconds=LOCK_TTL_SECONDS),
            }
        )

    def complete(self, lock_id: Any, response: dict[str, Any]) -> dict[str, Any]:
        return self.repository.complete(lock_id, response, now_utc())

    def fail(self, lock_id: Any, error_detail: str) -> dict[str, Any]:
        return self.repository.fail(lock_id, error_detail, now_utc())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
