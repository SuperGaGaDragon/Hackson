"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from hashlib import sha256
from typing import Any, Protocol

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
        documents = self.repository.list_memory_cards(user_id, scope, owner_type, owner_id, safe_limit)
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
            for document in documents
        ]


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
