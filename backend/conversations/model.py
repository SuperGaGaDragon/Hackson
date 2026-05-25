"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from datetime import datetime, timezone
from typing import Any


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def public_conversation(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a MongoDB conversation document into a public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "mode": document["mode"],
        "status": document["status"],
        "title": document.get("title"),
        "participantSlots": document.get("participant_slots", []),
        "parentConversationId": document.get("parent_conversation_id"),
        "messageCount": document.get("message_count", 0),
        "lastMessageAt": document.get("last_message_at"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_message(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a MongoDB message document into a public API shape."""
    return {
        "id": str(document["_id"]),
        "conversationId": str(document["conversation_id"]),
        "userId": document["user_id"],
        "mode": document["mode"],
        "sequence": document["sequence"],
        "senderType": document["sender_type"],
        "senderId": document.get("sender_id"),
        "senderSlot": document.get("sender_slot"),
        "role": document["role"],
        "content": document["content"],
        "contentType": document.get("content_type", "text"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
    }
