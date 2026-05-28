"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from hashlib import sha256
from typing import Any, Protocol

from fastapi import HTTPException, status

from conversations.model import now_utc
from context.schemas import MemoryCardSnapshot
from memory.governor import MemoryGovernor
from memory.model import public_memory_card
from memory.schemas import MemoryCandidate


class MemoryRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def upsert_memory_card(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def list_memory_cards(
        self,
        user_id: str,
        scope: str,
        owner_type: str | None,
        owner_id: str | None,
        limit: int,
    ) -> list[dict[str, Any]]: ...
    def list_user_memory_cards(self, user_id: str, include_deleted: bool, limit: int) -> list[dict[str, Any]]: ...
    def find_memory_card(self, user_id: str, memory_id: str) -> dict[str, Any] | None: ...
    def update_memory_status(
        self,
        user_id: str,
        memory_id: str,
        status: str,
        timestamp,
    ) -> dict[str, Any] | None: ...


class MemoryService:
    """Business rules for accepted long-term memory cards."""

    def __init__(self, repository: MemoryRepositoryProtocol, governor: MemoryGovernor | None = None):
        self.repository = repository
        self.governor = governor or MemoryGovernor()
        self.repository.ensure_indexes()

    def accept_candidate(self, user_id: str, candidate: MemoryCandidate) -> dict[str, Any] | None:
        if not self.governor.should_accept(candidate):
            return None
        timestamp = now_utc()
        document = {
            "user_id": user_id,
            "scope": candidate.scope,
            "owner_type": candidate.owner_type,
            "owner_id": candidate.owner_id,
            "memory_type": candidate.memory_type,
            "summary": candidate.summary,
            "source_message_ids": candidate.source_message_ids,
            "importance_score": candidate.importance_score,
            "confidence": candidate.confidence,
            "status": "active",
            "metadata": candidate.metadata,
            "dedupe_hash": _dedupe_hash(user_id, candidate),
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        return public_memory_card(self.repository.upsert_memory_card(document))

    def list_context_memory(
        self,
        user_id: str,
        scope: str,
        owner_type: str | None = None,
        owner_id: str | None = None,
        limit: int = 5,
    ) -> list[MemoryCardSnapshot]:
        safe_limit = min(max(limit, 1), 20)
        fetch_limit = min(safe_limit * 3, 60)
        documents = self.repository.list_memory_cards(user_id, scope, owner_type, owner_id, fetch_limit)
        documents = [document for document in documents if not _is_deprecated_generic_memory(document)]
        return [
            MemoryCardSnapshot(
                id=str(document["_id"]),
                scope=document["scope"],
                owner_type=document["owner_type"],
                owner_id=document["owner_id"],
                memory_type=document["memory_type"],
                summary=document["summary"],
                source_message_ids=document.get("source_message_ids", []),
                importance_score=document.get("importance_score", 0),
                confidence=document.get("confidence", 0),
            )
            for document in documents[:safe_limit]
        ]

    def list_account_context_memory(self, user_id: str, limit: int = 8) -> list[MemoryCardSnapshot]:
        """Return account-visible memory with legacy continuity fallbacks.

        V1 originally stored user preferences under `companion` and Agent-pair
        relationship summaries under `idle`. Until those rows are migrated, the
        account continuity reader treats them as account-visible input while
        leaving Work task memory private.
        """

        safe_limit = min(max(limit, 1), 20)
        documents: list[dict[str, Any]] = []
        documents.extend(self.repository.list_memory_cards(user_id, "account", None, None, safe_limit * 2))
        documents.extend(
            self.repository.list_memory_cards(
                user_id,
                "companion",
                "user",
                user_id,
                safe_limit,
            )
        )
        documents.extend(
            self.repository.list_memory_cards(
                user_id,
                "idle",
                "agent_pair",
                "agent_1:agent_2",
                safe_limit,
            )
        )
        documents = [document for document in _dedupe_documents(documents) if not _is_deprecated_generic_memory(document)]
        documents = sorted(
            documents,
            key=lambda document: (document.get("importance_score", 0), document.get("updated_at")),
            reverse=True,
        )
        return [_memory_snapshot(document) for document in documents[:safe_limit]]

    def list_user_memory(
        self,
        user_id: str,
        *,
        include_deleted: bool = False,
        limit: int = 50,
    ) -> dict[str, Any]:
        safe_limit = min(max(limit, 1), 100)
        fetch_limit = min(safe_limit * 3, 300)
        documents = self.repository.list_user_memory_cards(user_id, include_deleted, fetch_limit)
        documents = [document for document in documents if not _is_deprecated_generic_memory(document)]
        return {"memoryCards": [public_memory_card(document) for document in documents[:safe_limit]]}

    def update_status(self, user_id: str, memory_id: str, status_value: str) -> dict[str, Any]:
        if status_value not in {"active", "disabled", "archived"}:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="unsupported_memory_status",
            )
        document = self.repository.update_memory_status(user_id, memory_id, status_value, now_utc())
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="memory_not_found")
        return public_memory_card(document)

    def delete_memory(self, user_id: str, memory_id: str) -> dict[str, bool]:
        document = self.repository.update_memory_status(user_id, memory_id, "deleted", now_utc())
        if document is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="memory_not_found")
        return {"deletedMemoryCard": True}


def _dedupe_hash(user_id: str, candidate: MemoryCandidate) -> str:
    normalized = " ".join(candidate.summary.lower().split())
    raw = "|".join(
        [
            user_id,
            candidate.scope,
            candidate.owner_type,
            candidate.owner_id,
            candidate.memory_type,
            normalized,
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _memory_snapshot(document: dict[str, Any]) -> MemoryCardSnapshot:
    return MemoryCardSnapshot(
        id=str(document["_id"]),
        scope=document["scope"],
        owner_type=document["owner_type"],
        owner_id=document["owner_id"],
        memory_type=document["memory_type"],
        summary=document["summary"],
        source_message_ids=document.get("source_message_ids", []),
        importance_score=document.get("importance_score", 0),
        confidence=document.get("confidence", 0),
    )


def _dedupe_documents(documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for document in documents:
        key = str(document.get("_id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(document)
    return deduped


def _is_deprecated_generic_memory(document: dict[str, Any]) -> bool:
    return (
        document.get("scope") == "idle"
        and document.get("memory_type") == "relationship"
        and document.get("summary") == "Nora and Vale shared another idle interaction."
    )
