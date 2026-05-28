"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from conversations.schemas import ConversationResponse, MessageResponse


class InteractionUserMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    target_agent_id: str | None = Field(default=None, alias="targetAgentId")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdleTickRequest(BaseModel):
    target_agent_id: str | None = Field(default=None, alias="targetAgentId")
    idle_seed: str | None = Field(default=None, alias="idleSeed", max_length=1000)
    discussion_direction: str | None = Field(default=None, alias="discussionDirection", max_length=1000)
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey", max_length=120)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdleUserMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    discussion_direction: str | None = Field(default=None, alias="discussionDirection", max_length=1000)
    idempotency_key: str | None = Field(default=None, alias="idempotencyKey", max_length=120)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ContextDebugResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt_hash: str = Field(alias="promptHash")
    context_package_id: str | None = Field(default=None, alias="contextPackageId")
    token_estimate: int = Field(alias="tokenEstimate")
    model_name: str = Field(alias="modelName")
    orchestration_policy: str | None = Field(default=None, alias="orchestrationPolicy")
    reasoning_effort: str | None = Field(default=None, alias="reasoningEffort")


class InteractionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    conversation: ConversationResponse
    user_message: MessageResponse | None = Field(default=None, alias="userMessage")
    agent_message: MessageResponse = Field(alias="agentMessage")
    context: ContextDebugResponse
