"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from context.schemas import ContextMode, ContextPackage


ReasoningEffort = Literal["minimal", "low", "medium", "high"]
ToolPolicy = Literal["disabled", "auto_search"]


class OrchestrationPolicy(BaseModel):
    """Mode-specific policy chosen before provider execution."""

    name: str
    reasoning_effort: ReasoningEffort
    max_output_tokens: int
    temperature: float
    tool_policy: ToolPolicy = "disabled"


class OrchestrationRequest(BaseModel):
    """Product-level generation request consumed by Hackson Orchestrator."""

    mode: ContextMode
    user_id: str
    conversation_id: str
    target_agent_id: str
    context_package: ContextPackage
    metadata: dict[str, Any] = Field(default_factory=dict)


class OrchestrationResponse(BaseModel):
    """Normalized generation result returned to interaction flows."""

    text: str
    model_name: str
    provider: str
    policy_name: str
    reasoning_effort: ReasoningEffort
    tool_policy: ToolPolicy
    provider_response_id: str | None = None
    reasoning_summary: str | None = None
    tool_events: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
