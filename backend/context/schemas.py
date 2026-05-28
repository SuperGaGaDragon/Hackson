"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ContextMode(str, Enum):
    IDLE = "idle"
    COMPANION_1 = "companion_1"
    COMPANION_2 = "companion_2"
    WORK = "work"


class SenderType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    TOOL = "tool"


class ModelMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AgentPersonaSnapshot(BaseModel):
    """Read-only Agent persona shape consumed by context.

    The agents module owns persistence and mutation. Context receives this
    snapshot and must never modify Agent source records.
    """

    id: str
    name: str
    core_persona: str
    speaking_style: str | None = None
    episode_state: str | None = None

    @field_validator("core_persona")
    @classmethod
    def require_core_persona(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("core_persona_required")
        return value


class ConversationMessage(BaseModel):
    id: str | None = None
    sender_type: SenderType
    sender_id: str | None = None
    sender_name: str | None = None
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def require_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message_content_required")
        return value


class ConversationSummary(BaseModel):
    id: str | None = None
    summary_type: str
    content: str

    @field_validator("content")
    @classmethod
    def require_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("summary_content_required")
        return value


class MemoryCardSnapshot(BaseModel):
    id: str
    scope: Literal["idle", "companion", "work"]
    owner_type: str
    owner_id: str
    memory_type: str
    summary: str
    source_message_ids: list[str] = Field(default_factory=list)
    importance_score: float = 0.5
    confidence: float = 0.5

    @field_validator("summary")
    @classmethod
    def require_summary(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("memory_summary_required")
        return value


class UserProfileSnapshot(BaseModel):
    id: str
    username: str | None = None
    display_name: str | None = None
    language_preference: str | None = "zh"
    personality: str | None = None
    story: str | None = None


class ContextBuildInput(BaseModel):
    mode: ContextMode
    conversation_id: str
    target_agent_id: str
    agents: list[AgentPersonaSnapshot]
    recent_messages: list[ConversationMessage] = Field(default_factory=list)
    summary: ConversationSummary | None = None
    user_message: str | None = None
    user_profile: UserProfileSnapshot | None = None
    user_direction: str | None = None
    idle_seed: str | None = None
    idle_recent_messages: list[ConversationMessage] = Field(default_factory=list)
    idle_summary: ConversationSummary | None = None
    memory_cards: list[MemoryCardSnapshot] = Field(default_factory=list)
    task_state: dict[str, Any] | None = None
    token_budget: int | None = None


class ContextPackage(BaseModel):
    id: str | None = None
    mode: ContextMode
    conversation_id: str
    agent_id: str
    messages: list[ModelMessage]
    included_message_ids: list[str] = Field(default_factory=list)
    included_summary_ids: list[str] = Field(default_factory=list)
    included_memory_ids: list[str] = Field(default_factory=list)
    included_agent_ids: list[str] = Field(default_factory=list)
    token_estimate: int
    prompt_hash: str
    recipe_version: str = "context_runtime_v1"
    full_prompt_logging_enabled: bool = False
    full_prompt_text_stored: bool = False
    debug_notes: list[str] = Field(default_factory=list)
