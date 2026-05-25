"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from context.compaction import select_recent_messages
from context.schemas import ConversationMessage, ConversationSummary


def build_transition_context(
    *,
    user_message: str,
    idle_recent_messages: list[ConversationMessage],
    idle_summary: ConversationSummary | None,
) -> str:
    """Generate the explicit handoff required when a user joins idle."""
    topic_summary = _topic_summary(idle_recent_messages, idle_summary)
    return "\n".join(
        [
            "用户刚刚加入了两个 Agent 正在进行的 idle 对话。",
            f"它们刚才正在讨论：{topic_summary}",
            f"用户说：{user_message.strip()}",
            "现在 Agent 必须把注意力转向用户，同时保留刚才话题的连续性。",
            "回复必须明确回应用户，不能继续无视用户只和另一个 Agent 对话。",
        ]
    )


def _topic_summary(
    idle_recent_messages: list[ConversationMessage],
    idle_summary: ConversationSummary | None,
) -> str:
    if idle_summary is not None:
        return idle_summary.content

    selected = select_recent_messages(idle_recent_messages, limit=4)
    if not selected:
        return "当前没有可用的 idle 摘要，用户加入了一个刚开始的场景。"

    lines = []
    for message in selected:
        speaker = message.sender_name or message.sender_id or message.sender_type.value
        lines.append(f"{speaker}: {message.content}")
    return " / ".join(lines)

