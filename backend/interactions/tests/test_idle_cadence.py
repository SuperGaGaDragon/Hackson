"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest import TestCase

from interactions.idle_cadence import IdleCadenceService


class FakeIdleRunnerStateRepository:
    def __init__(self) -> None:
        self.rows: dict[tuple[str, str], dict[str, Any]] = {}
        self.indexes_ready = False

    def ensure_indexes(self) -> None:
        self.indexes_ready = True

    def get_state(self, user_id: str, conversation_id: str) -> dict[str, Any] | None:
        return self.rows.get((user_id, conversation_id))

    def upsert_state(self, user_id: str, conversation_id: str, changes: dict[str, Any]) -> dict[str, Any]:
        row = {
            **self.rows.get((user_id, conversation_id), {}),
            **changes,
            "user_id": user_id,
            "conversation_id": conversation_id,
        }
        self.rows[(user_id, conversation_id)] = row
        return row


class IdleCadenceServiceTest(TestCase):
    def setUp(self) -> None:
        self.repository = FakeIdleRunnerStateRepository()
        self.service = IdleCadenceService(self.repository, daily_limit=2)
        self.now = datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)
        self.user = {"id": "user_1", "backgroundIdleOn": True}
        self.conversation = {"id": "conv_1", "mode": "idle", "status": "active"}

    def test_background_idle_disabled_blocks_browser_closed_tick(self) -> None:
        decision = self.service.background_tick_decision(
            user={"id": "user_1", "backgroundIdleOn": False},
            conversation=self.conversation,
            now=self.now,
        )

        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "background_idle_disabled")

    def test_enabled_background_idle_allows_inside_budget(self) -> None:
        decision = self.service.background_tick_decision(
            user=self.user,
            conversation=self.conversation,
            now=self.now,
        )

        self.assertTrue(decision["allowed"])
        self.assertEqual(decision["dailyTurnsRemaining"], 2)

    def test_background_idle_respects_daily_budget(self) -> None:
        self.service.record_background_tick_result(
            user_id="user_1",
            conversation_id="conv_1",
            succeeded=True,
            now=self.now,
        )
        self.service.record_background_tick_result(
            user_id="user_1",
            conversation_id="conv_1",
            succeeded=True,
            now=self.now,
        )

        decision = self.service.background_tick_decision(
            user=self.user,
            conversation=self.conversation,
            now=self.now,
        )

        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "idle_budget_exhausted")

    def test_provider_failure_moves_runner_to_cooldown(self) -> None:
        cooldown_until = self.now + timedelta(minutes=10)
        self.service.record_background_tick_result(
            user_id="user_1",
            conversation_id="conv_1",
            succeeded=False,
            cooldown_until=cooldown_until,
            now=self.now,
        )

        decision = self.service.background_tick_decision(
            user=self.user,
            conversation=self.conversation,
            now=self.now + timedelta(minutes=1),
        )

        self.assertFalse(decision["allowed"])
        self.assertEqual(decision["reason"], "idle_cooldown")
        self.assertEqual(decision["cooldownUntil"], cooldown_until)
