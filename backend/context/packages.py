"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from hashlib import sha256

from context.schemas import ContextMode, ContextPackage, ModelMessage


def estimate_tokens(text: str) -> int:
    """Cheap deterministic token estimate for budgeting and package logs."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list[ModelMessage]) -> int:
    return sum(estimate_tokens(message.content) for message in messages)


def prompt_hash(messages: list[ModelMessage]) -> str:
    raw = "\n\n".join(f"{message.role}:{message.content}" for message in messages)
    return sha256(raw.encode("utf-8")).hexdigest()


def render_prompt_text(messages: list[ModelMessage]) -> str:
    """Render the complete model-visible messages for optional prompt logging."""
    return "\n\n".join(f"{message.role}:\n{message.content}" for message in messages)


def build_context_package(
    *,
    mode: ContextMode,
    conversation_id: str,
    agent_id: str,
    messages: list[ModelMessage],
    included_message_ids: list[str],
    included_summary_ids: list[str],
    included_memory_ids: list[str] | None = None,
    included_agent_ids: list[str],
    debug_notes: list[str] | None = None,
) -> ContextPackage:
    return ContextPackage(
        mode=mode,
        conversation_id=conversation_id,
        agent_id=agent_id,
        messages=messages,
        included_message_ids=included_message_ids,
        included_summary_ids=included_summary_ids,
        included_memory_ids=included_memory_ids or [],
        included_agent_ids=included_agent_ids,
        token_estimate=estimate_messages_tokens(messages),
        prompt_hash=prompt_hash(messages),
        debug_notes=debug_notes or [],
    )
