"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from context.schemas import ContextMode
from orchestration.policies import policy_for_mode


class OrchestrationPolicyTest(TestCase):
    def test_idle_uses_low_reasoning_and_small_output_budget(self) -> None:
        policy = policy_for_mode(ContextMode.IDLE)

        self.assertEqual(policy.name, "idle_quality_v1")
        self.assertEqual(policy.reasoning_effort, "low")
        self.assertEqual(policy.max_output_tokens, 360)
        self.assertEqual(policy.tool_policy, "disabled")

    def test_companion_1_uses_transition_quality_policy(self) -> None:
        policy = policy_for_mode(ContextMode.COMPANION_1)

        self.assertEqual(policy.name, "companion_join_quality_v1")
        self.assertEqual(policy.reasoning_effort, "medium")
        self.assertEqual(policy.max_output_tokens, 520)
        self.assertEqual(policy.tool_policy, "disabled")

    def test_companion_2_uses_chat_quality_policy(self) -> None:
        policy = policy_for_mode(ContextMode.COMPANION_2)

        self.assertEqual(policy.name, "companion_chat_quality_v1")
        self.assertEqual(policy.reasoning_effort, "medium")
        self.assertEqual(policy.max_output_tokens, 700)
        self.assertEqual(policy.tool_policy, "disabled")
