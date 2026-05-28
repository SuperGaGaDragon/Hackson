"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class RuntimeMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelRuntimeConfig(BaseModel):
    provider: Literal["openai_compatible", "codex_cli"] = "openai_compatible"
    base_url: str = "https://api.openai.com/v1"
    model_name: str
    api_key: str = Field(repr=False, exclude=True)
    api_mode: Literal["chat_completions", "responses"] = "chat_completions"
    timeout_seconds: float = 60.0
    max_output_tokens: int = 1024
    temperature: float = 0.7
    codex_command: str = "codex"
    codex_home: str | None = None


class ModelGenerateRequest(BaseModel):
    messages: list[RuntimeMessage]
    max_output_tokens: int | None = None
    temperature: float | None = None
    timeout_seconds: float | None = None
    reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = None
    tool_policy: Literal["disabled", "auto_search"] | None = None
    use_responses_api: bool | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelGenerateResponse(BaseModel):
    text: str
    model_name: str
    provider: str
    provider_response_id: str | None = None
    reasoning_summary: str | None = None
    tool_events: list[dict[str, Any]] = Field(default_factory=list)
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
