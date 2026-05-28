"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime, timezone
from typing import Any, Protocol


DEFAULT_DAILY_BACKGROUND_TURN_LIMIT = 24


class IdleRunnerStateRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def get_state(self, user_id: str, conversation_id: str) -> dict[str, Any] | None: ...
    def upsert_state(self, user_id: str, conversation_id: str, changes: dict[str, Any]) -> dict[str, Any]: ...


class IdleCadenceService:
    """Server-side gate for future Background Idle runner attempts."""

    def __init__(
        self,
        repository: IdleRunnerStateRepositoryProtocol,
        daily_limit: int = DEFAULT_DAILY_BACKGROUND_TURN_LIMIT,
    ):
        self.repository = repository
        self.daily_limit = daily_limit
        self.repository.ensure_indexes()

    def background_tick_decision(
        self,
        *,
        user: dict[str, Any],
        conversation: dict[str, Any] | None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        timestamp = now or now_utc()
        if not user.get("backgroundIdleOn", False):
            return _blocked("background_idle_disabled", timestamp)
        if conversation is None or conversation.get("mode") != "idle" or conversation.get("status") != "active":
            return _blocked("idle_conversation_unavailable", timestamp)

        state = self.repository.get_state(user["id"], conversation["id"]) or {}
        cooldown_until = state.get("cooldown_until")
        if cooldown_until is not None and cooldown_until > timestamp:
            return _blocked("idle_cooldown", timestamp, cooldown_until=cooldown_until)

        window_day = timestamp.date().isoformat()
        used_day = state.get("budget_day")
        used_count = state.get("daily_turns", 0) if used_day == window_day else 0
        if used_count >= self.daily_limit:
            return _blocked("idle_budget_exhausted", timestamp)

        return {
            "allowed": True,
            "reason": "allowed",
            "checkedAt": timestamp,
            "dailyTurnsRemaining": self.daily_limit - used_count,
            "cooldownUntil": None,
        }

    def record_background_tick_result(
        self,
        *,
        user_id: str,
        conversation_id: str,
        succeeded: bool,
        cooldown_until: datetime | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        timestamp = now or now_utc()
        state = self.repository.get_state(user_id, conversation_id) or {}
        window_day = timestamp.date().isoformat()
        prior_count = state.get("daily_turns", 0) if state.get("budget_day") == window_day else 0
        changes: dict[str, Any] = {
            "budget_day": window_day,
            "updated_at": timestamp,
        }
        if succeeded:
            changes["daily_turns"] = prior_count + 1
            changes["cooldown_until"] = None
        else:
            changes["daily_turns"] = prior_count
            changes["cooldown_until"] = cooldown_until
        return self.repository.upsert_state(user_id, conversation_id, changes)


def _blocked(reason: str, timestamp: datetime, cooldown_until: datetime | None = None) -> dict[str, Any]:
    return {
        "allowed": False,
        "reason": reason,
        "checkedAt": timestamp,
        "dailyTurnsRemaining": 0,
        "cooldownUntil": cooldown_until,
    }


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
