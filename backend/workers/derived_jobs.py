"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime
from typing import Any, Callable, Literal, Protocol

from fastapi import HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ASCENDING, DESCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database

from conversations.model import now_utc

DerivedJobType = Literal["summary", "memory_candidate", "diary", "relationship"]
DerivedJobStatus = Literal["pending", "running", "succeeded", "failed"]


class DerivedJobCreateRequest(BaseModel):
    job_type: DerivedJobType = Field(alias="jobType")
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    source_message_ids: list[str] = Field(alias="sourceMessageIds")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(populate_by_name=True)


class DerivedJob(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    job_type: DerivedJobType = Field(alias="jobType")
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    source_message_ids: list[str] = Field(alias="sourceMessageIds")
    status: DerivedJobStatus
    attempt_count: int = Field(alias="attemptCount")
    last_error: str | None = Field(default=None, alias="lastError")
    metadata: dict[str, Any]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class DerivedJobRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create_job(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_pending_jobs(self, limit: int) -> list[dict[str, Any]]: ...
    def mark_job_running(self, job_id: str) -> dict[str, Any] | None: ...
    def mark_job_succeeded(self, job_id: str) -> dict[str, Any] | None: ...
    def mark_job_failed(self, job_id: str, error: str) -> dict[str, Any] | None: ...


class DerivedJobRepository:
    """MongoDB persistence for best-effort derived work jobs."""

    def __init__(self, database: Database):
        self.derived_jobs: Collection = database["derived_jobs"]

    def ensure_indexes(self) -> None:
        self.derived_jobs.create_index([("status", ASCENDING), ("created_at", ASCENDING)])
        self.derived_jobs.create_index([("user_id", ASCENDING), ("conversation_id", ASCENDING), ("created_at", DESCENDING)])
        self.derived_jobs.create_index([("source_message_ids", ASCENDING)])

    def create_job(self, document: dict[str, Any]) -> dict[str, Any]:
        result = self.derived_jobs.insert_one(document)
        created = self.derived_jobs.find_one({"_id": result.inserted_id})
        assert created is not None
        return created

    def find_pending_jobs(self, limit: int) -> list[dict[str, Any]]:
        return list(self.derived_jobs.find({"status": "pending"}).sort("created_at", ASCENDING).limit(limit))

    def mark_job_running(self, job_id: str) -> dict[str, Any] | None:
        return self._mark(job_id, {"status": "running", "$inc": {"attempt_count": 1}})

    def mark_job_succeeded(self, job_id: str) -> dict[str, Any] | None:
        return self._mark(job_id, {"status": "succeeded", "last_error": None})

    def mark_job_failed(self, job_id: str, error: str) -> dict[str, Any] | None:
        return self._mark(job_id, {"status": "failed", "last_error": error})

    def _mark(self, job_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
        from bson import ObjectId

        if not ObjectId.is_valid(job_id):
            query_id: Any = job_id
        else:
            query_id = ObjectId(job_id)
        increment = values.pop("$inc", None)
        update: dict[str, Any] = {"$set": {**values, "updated_at": now_utc()}}
        if increment:
            update["$inc"] = increment
        return self.derived_jobs.find_one_and_update({"_id": query_id}, update, return_document=ReturnDocument.AFTER)


class DerivedJobService:
    """Best-effort orchestration for async derived work."""

    def __init__(self, repository: DerivedJobRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def enqueue(self, payload: DerivedJobCreateRequest) -> dict[str, Any]:
        if not payload.source_message_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="derived_job_requires_source_messages",
            )
        timestamp = now_utc()
        document = {
            "job_type": payload.job_type,
            "user_id": payload.user_id,
            "conversation_id": payload.conversation_id,
            "source_message_ids": payload.source_message_ids,
            "status": "pending",
            "attempt_count": 0,
            "last_error": None,
            "metadata": payload.metadata,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return _public_job(self.repository.create_job(document))

    def run_pending(self, handlers: dict[str, Callable[[DerivedJob], None]], limit: int = 10) -> int:
        processed = 0
        for document in self.repository.find_pending_jobs(min(max(limit, 1), 100)):
            job = _job_snapshot(document)
            self.repository.mark_job_running(job.id)
            try:
                handler = handlers.get(job.job_type)
                if handler is None:
                    raise RuntimeError(f"missing_handler:{job.job_type}")
                handler(job)
            except Exception as exc:  # best-effort worker failures must not escape
                self.repository.mark_job_failed(job.id, str(exc))
            else:
                self.repository.mark_job_succeeded(job.id)
            processed += 1
        return processed


def _public_job(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["_id"]),
        "jobType": document["job_type"],
        "userId": document["user_id"],
        "conversationId": document["conversation_id"],
        "sourceMessageIds": document.get("source_message_ids", []),
        "status": document["status"],
        "attemptCount": document.get("attempt_count", 0),
        "lastError": document.get("last_error"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def _job_snapshot(document: dict[str, Any]) -> DerivedJob:
    return DerivedJob(**_public_job(document))
