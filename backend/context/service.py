"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from context.packages import render_prompt_text
from context.schemas import ContextPackage


PROMPT_LOG_RETENTION_DAYS = 30


class ContextPackageRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def list_prompt_logs(self, user_id: str, limit: int) -> list[dict[str, Any]]: ...
    def clear_prompt_text(self, user_id: str, timestamp: datetime) -> int: ...
    def clear_expired_prompt_text(self, timestamp: datetime) -> int: ...


class ContextPackageService:
    """Persist context package audit records and user-owned prompt logs."""

    def __init__(self, repository: ContextPackageRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def persist_package(
        self,
        *,
        user_id: str,
        package: ContextPackage,
        full_prompt_logging_enabled: bool,
    ) -> dict[str, Any]:
        timestamp = now_utc()
        self.repository.clear_expired_prompt_text(timestamp)
        full_prompt_text = render_prompt_text(package.messages) if full_prompt_logging_enabled else None
        full_prompt_text_expires_at = (
            timestamp + timedelta(days=PROMPT_LOG_RETENTION_DAYS) if full_prompt_text is not None else None
        )
        document = {
            "user_id": user_id,
            "mode": package.mode.value,
            "conversation_id": package.conversation_id,
            "target_agent_id": package.agent_id,
            "prompt_hash": package.prompt_hash,
            "token_estimate": package.token_estimate,
            "recipe_version": package.recipe_version,
            "included_message_ids": list(package.included_message_ids),
            "included_summary_ids": list(package.included_summary_ids),
            "included_memory_ids": list(package.included_memory_ids),
            "included_agent_ids": list(package.included_agent_ids),
            "debug_notes": list(package.debug_notes),
            "full_prompt_logging_enabled": full_prompt_logging_enabled,
            "full_prompt_text": full_prompt_text,
            "full_prompt_text_expires_at": full_prompt_text_expires_at,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        created = self.repository.create(document)
        public = public_context_package(created, include_prompt_text=True)
        package.id = public["id"]
        package.full_prompt_logging_enabled = full_prompt_logging_enabled
        package.full_prompt_text_stored = bool(full_prompt_text)
        return public

    def list_prompt_logs(self, user_id: str, limit: int = 20) -> dict[str, Any]:
        self.repository.clear_expired_prompt_text(now_utc())
        rows = self.repository.list_prompt_logs(user_id, limit)
        return {"promptLogs": [public_context_package(row, include_prompt_text=True) for row in rows]}

    def delete_prompt_logs(self, user_id: str) -> dict[str, int]:
        timestamp = now_utc()
        return {"deletedPromptLogs": self.repository.clear_prompt_text(user_id, timestamp)}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def public_context_package(document: dict[str, Any], *, include_prompt_text: bool = False) -> dict[str, Any]:
    full_prompt_text = document.get("full_prompt_text")
    record = {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "mode": document["mode"],
        "conversationId": document["conversation_id"],
        "targetAgentId": document["target_agent_id"],
        "promptHash": document["prompt_hash"],
        "tokenEstimate": document["token_estimate"],
        "recipeVersion": document.get("recipe_version", "context_runtime_v1"),
        "includedMessageIds": document.get("included_message_ids", []),
        "includedSummaryIds": document.get("included_summary_ids", []),
        "includedMemoryIds": document.get("included_memory_ids", []),
        "includedAgentIds": document.get("included_agent_ids", []),
        "debugNotes": document.get("debug_notes", []),
        "fullPromptLoggingEnabled": document.get("full_prompt_logging_enabled", False),
        "fullPromptTextStored": bool(full_prompt_text),
        "fullPromptTextExpiresAt": document.get("full_prompt_text_expires_at"),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }
    if include_prompt_text:
        record["fullPromptText"] = full_prompt_text
    return record
