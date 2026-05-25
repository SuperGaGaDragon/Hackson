"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from context.packages import estimate_tokens
from context.schemas import ConversationMessage, ConversationSummary

DEFAULT_RECENT_MESSAGE_LIMIT = 12


def select_recent_messages(
    messages: list[ConversationMessage],
    *,
    limit: int = DEFAULT_RECENT_MESSAGE_LIMIT,
    token_budget: int | None = None,
) -> list[ConversationMessage]:
    """Keep the newest messages while respecting a rough token budget."""
    if limit <= 0:
        return []

    selected = list(messages[-limit:])
    if token_budget is None:
        return selected

    trimmed: list[ConversationMessage] = []
    used_tokens = 0
    for message in reversed(selected):
        message_tokens = estimate_tokens(message.content)
        if trimmed and used_tokens + message_tokens > token_budget:
            break
        if not trimmed and message_tokens > token_budget:
            trimmed.append(message)
            break
        trimmed.append(message)
        used_tokens += message_tokens
    return list(reversed(trimmed))


def summary_block(summary: ConversationSummary | None) -> str | None:
    if summary is None:
        return None
    return f"{summary.summary_type} summary:\n{summary.content}"

