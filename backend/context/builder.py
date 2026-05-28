"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from context.packages import build_context_package
from context.recipes import (
    build_companion_1_messages,
    build_companion_2_messages,
    build_idle_messages,
    build_work_messages,
)
from context.schemas import ContextBuildInput, ContextMode, ContextPackage, ConversationMessage


class ContextBuilder:
    """Build model-ready context packages without calling models or databases."""

    def build(self, input_data: ContextBuildInput) -> ContextPackage:
        messages = self._build_messages(input_data)
        included_messages = _included_message_ids(input_data)
        included_summaries = _included_summary_ids(input_data)
        included_memory = _included_memory_ids(input_data)
        included_agents = [agent.id for agent in input_data.agents]
        return build_context_package(
            mode=input_data.mode,
            conversation_id=input_data.conversation_id,
            agent_id=input_data.target_agent_id,
            messages=messages,
            included_message_ids=included_messages,
            included_summary_ids=included_summaries,
            included_memory_ids=included_memory,
            included_agent_ids=included_agents,
            debug_notes=_debug_notes(input_data),
        )

    def _build_messages(self, input_data: ContextBuildInput):
        if input_data.mode == ContextMode.IDLE:
            return build_idle_messages(input_data)
        if input_data.mode == ContextMode.COMPANION_1:
            return build_companion_1_messages(input_data)
        if input_data.mode == ContextMode.COMPANION_2:
            return build_companion_2_messages(input_data)
        if input_data.mode == ContextMode.WORK:
            return build_work_messages(input_data)
        raise ValueError("unsupported_context_mode")


def _included_message_ids(input_data: ContextBuildInput) -> list[str]:
    messages: list[ConversationMessage] = []
    if input_data.mode == ContextMode.COMPANION_1:
        messages.extend(input_data.recent_messages)
        messages.extend(input_data.idle_recent_messages)
    else:
        messages.extend(input_data.recent_messages)
    return [message.id for message in messages if message.id]


def _included_summary_ids(input_data: ContextBuildInput) -> list[str]:
    summaries = [input_data.summary, input_data.idle_summary]
    return [summary.id for summary in summaries if summary is not None and summary.id]


def _debug_notes(input_data: ContextBuildInput) -> list[str]:
    notes = [f"mode={input_data.mode.value}"]
    if input_data.mode == ContextMode.COMPANION_1:
        notes.append("transition_context=enabled")
    if input_data.summary is not None or input_data.idle_summary is not None:
        notes.append("summary=enabled")
    if _included_memory_ids(input_data):
        notes.append("memory=enabled")
    if input_data.token_budget is not None:
        notes.append(f"token_budget={input_data.token_budget}")
    return notes


def _included_memory_ids(input_data: ContextBuildInput) -> list[str]:
    if input_data.mode == ContextMode.IDLE:
        allowed_scopes = {"account", "idle"}
    elif input_data.mode == ContextMode.COMPANION_1:
        allowed_scopes = {"account", "idle", "companion"}
    elif input_data.mode == ContextMode.COMPANION_2:
        allowed_scopes = {"account", "idle", "companion"}
    elif input_data.mode == ContextMode.WORK:
        allowed_scopes = {"account", "work"}
    else:
        allowed_scopes = set()
    return [memory.id for memory in input_data.memory_cards if memory.scope in allowed_scopes]
