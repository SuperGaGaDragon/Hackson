"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any


def public_memory_card(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a memory card persistence document to the public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "scope": document["scope"],
        "ownerType": document["owner_type"],
        "ownerId": document["owner_id"],
        "memoryType": document["memory_type"],
        "summary": document["summary"],
        "sourceMessageIds": document.get("source_message_ids", []),
        "importanceScore": document.get("importance_score", 0),
        "confidence": document.get("confidence", 0),
        "status": document.get("status", "active"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }
