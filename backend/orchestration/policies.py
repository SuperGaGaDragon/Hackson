"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from context.schemas import ContextMode
from orchestration.schemas import OrchestrationPolicy


IDLE_QUALITY_V1 = OrchestrationPolicy(
    name="idle_quality_v1",
    reasoning_effort="low",
    max_output_tokens=360,
    temperature=0.4,
    tool_policy="disabled",
)

COMPANION_JOIN_QUALITY_V1 = OrchestrationPolicy(
    name="companion_join_quality_v1",
    reasoning_effort="medium",
    max_output_tokens=520,
    temperature=0.45,
    tool_policy="disabled",
)

COMPANION_CHAT_QUALITY_V1 = OrchestrationPolicy(
    name="companion_chat_quality_v1",
    reasoning_effort="medium",
    max_output_tokens=700,
    temperature=0.5,
    tool_policy="disabled",
)

WORK_FALLBACK_CHAT_V1 = OrchestrationPolicy(
    name="work_fallback_chat_v1",
    reasoning_effort="medium",
    max_output_tokens=700,
    temperature=0.3,
    tool_policy="disabled",
)


def policy_for_mode(mode: ContextMode) -> OrchestrationPolicy:
    """Return the deterministic V1 orchestration policy for one mode."""
    if mode == ContextMode.IDLE:
        return IDLE_QUALITY_V1
    if mode == ContextMode.COMPANION_1:
        return COMPANION_JOIN_QUALITY_V1
    if mode == ContextMode.COMPANION_2:
        return COMPANION_CHAT_QUALITY_V1
    if mode == ContextMode.WORK:
        return WORK_FALLBACK_CHAT_V1
    raise ValueError("unsupported_orchestration_mode")
