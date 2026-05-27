"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import json
from typing import Any, Protocol

from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage
from work_mode.tool_protocol import ToolAction, ToolActionValidationError, parse_tool_action

RETRYABLE_MODEL_ERRORS = {"model_timeout", "model_rate_limited", "model_network_error", "model_unavailable"}


class ModelRuntimeProtocol(Protocol):
    def generate(self, request: ModelGenerateRequest): ...


class ToolActionClientError(RuntimeError):
    """Stable error from the JSON Action adapter."""

    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ToolActionClient:
    """Provider-agnostic JSON Action adapter over model_runtime."""

    def __init__(self, model_runtime: ModelRuntimeProtocol):
        self.model_runtime = model_runtime

    def generate_action(self, context: dict[str, Any]) -> ToolAction:
        try:
            response = self.model_runtime.generate(_action_request(context))
        except ModelRuntimeError as exc:
            code = str(exc)
            raise ToolActionClientError(code, code, retryable=code in RETRYABLE_MODEL_ERRORS) from exc

        try:
            return parse_tool_action(response.text)
        except ToolActionValidationError as exc:
            raise ToolActionClientError(exc.code, str(exc), retryable=False) from exc


def _action_request(context: dict[str, Any]) -> ModelGenerateRequest:
    return ModelGenerateRequest(
        messages=[
            RuntimeMessage(
                role="system",
                content=(
                    "You are the Work Mode Lead Agent runtime. Return exactly one JSON tool action. "
                    "Do not return plain assistant text. Do not wrap JSON in markdown. "
                    "Use only the available tools from the context."
                ),
            ),
            RuntimeMessage(
                role="user",
                content=json.dumps(context, ensure_ascii=False, sort_keys=True),
            ),
        ],
        max_output_tokens=1800,
        temperature=0.2,
        reasoning_effort="low",
    )
