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


def public_user(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a MongoDB user document into a public API shape."""
    return {
        "id": str(document["_id"]),
        "username": document["username"],
        "displayName": document["display_name"],
        "email": document["email"],
        "idleOn": document.get("idle_on", True),
        "languagePreference": document.get("language_preference", "zh"),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }
