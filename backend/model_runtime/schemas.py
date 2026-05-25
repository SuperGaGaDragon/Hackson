"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Literal

from pydantic import BaseModel, Field


class RuntimeMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ModelRuntimeConfig(BaseModel):
    provider: Literal["openai_compatible"] = "openai_compatible"
    base_url: str = "https://api.openai.com/v1"
    model_name: str
    api_key: str = Field(repr=False)
    timeout_seconds: float = 60.0
    max_output_tokens: int = 1024
    temperature: float = 0.7


class ModelGenerateRequest(BaseModel):
    messages: list[RuntimeMessage]
    max_output_tokens: int | None = None
    temperature: float | None = None


class ModelGenerateResponse(BaseModel):
    text: str
    model_name: str
    provider: str

