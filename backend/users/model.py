"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime, timezone
from typing import Any

from agents.catalog import normalize_user_agent_profiles


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
        "backgroundIdleOn": document.get("background_idle_on", False),
        "fullPromptLoggingOn": document.get("full_prompt_logging_on", True),
        "languagePreference": document.get("language_preference", "zh"),
        "personality": document.get("personality", ""),
        "story": document.get("story", ""),
        "agentProfiles": normalize_user_agent_profiles(document.get("agent_profiles")),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }
