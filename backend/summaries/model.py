"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any


def public_summary(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a summary persistence document to the public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "conversationId": document["conversation_id"],
        "summaryType": document["summary_type"],
        "content": document["content"],
        "sourceMessageStartId": document["source_message_start_id"],
        "sourceMessageEndId": document["source_message_end_id"],
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }
