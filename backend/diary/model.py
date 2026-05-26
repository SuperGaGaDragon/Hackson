"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any


def public_diary_entry(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a diary persistence document to the public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "agentId": document["agent_id"],
        "content": document["content"],
        "sourceMessageIds": document.get("source_message_ids", []),
        "createdAt": document["created_at"],
    }
