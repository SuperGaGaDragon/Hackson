"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import json
from datetime import date, datetime
from typing import Any, Protocol

from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage
from work_mode.tool_protocol import ToolAction, ToolActionValidationError, parse_tool_action

RETRYABLE_MODEL_ERRORS = {
    "model_timeout",
    "model_rate_limited",
    "model_network_error",
    "model_unavailable",
    "model_response_missing_text",
}
RETRYABLE_HTTP_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


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

    def __init__(self, model_runtime: ModelRuntimeProtocol, timeout_seconds: float | None = None):
        self.model_runtime = model_runtime
        self.timeout_seconds = timeout_seconds

    def generate_action(self, context: dict[str, Any]) -> ToolAction:
        try:
            response = self.model_runtime.generate(_action_request(context, timeout_seconds=self.timeout_seconds))
        except ModelRuntimeError as exc:
            code = exc.code
            raise ToolActionClientError(code, code, retryable=_is_retryable_model_error(exc)) from exc

        try:
            return parse_tool_action(response.text)
        except ToolActionValidationError as exc:
            raise ToolActionClientError(exc.code, str(exc), retryable=False) from exc


class DelegateResultClient:
    """Provider-agnostic structured result adapter for one-shot Delegate Agent windows."""

    def __init__(self, model_runtime: ModelRuntimeProtocol, timeout_seconds: float | None = None):
        self.model_runtime = model_runtime
        self.timeout_seconds = timeout_seconds

    def generate_delegate_result(self, context: dict[str, Any]) -> str:
        try:
            return self.model_runtime.generate(_delegate_request(context, timeout_seconds=self.timeout_seconds)).text
        except ModelRuntimeError as exc:
            raise ToolActionClientError(exc.code, exc.code, retryable=_is_retryable_model_error(exc)) from exc


def _action_request(context: dict[str, Any], timeout_seconds: float | None = None) -> ModelGenerateRequest:
    context_json = _context_json(context)
    return ModelGenerateRequest(
        messages=[
            RuntimeMessage(
                role="system",
                content=(
                    "You are the Work Mode Lead Agent runtime. Return exactly one JSON tool action. "
                    "The JSON must have top-level tool and arguments fields. "
                    "Use context.toolSchemas and context.toolExamples for exact camelCase argument names. "
                    "Do not return plain assistant text. Do not wrap JSON in markdown. "
                    "Use only the available tools from the context."
                ),
            ),
            RuntimeMessage(
                role="user",
                content=context_json,
            ),
        ],
        max_output_tokens=1800,
        temperature=0.2,
        timeout_seconds=timeout_seconds,
        reasoning_effort="low",
    )


def _delegate_request(context: dict[str, Any], timeout_seconds: float | None = None) -> ModelGenerateRequest:
    context_json = _context_json(context)
    return ModelGenerateRequest(
        messages=[
            RuntimeMessage(
                role="system",
                content=(
                    "You are the Work Mode Delegate Agent. Return exactly one JSON object with "
                    "status, title, summary, content, and reason. Do not call tools. "
                    "Do not wrap JSON in markdown."
                ),
            ),
            RuntimeMessage(
                role="user",
                content=context_json,
            ),
        ],
        max_output_tokens=3000,
        temperature=0.45,
        timeout_seconds=timeout_seconds,
        reasoning_effort="low",
    )


def _is_retryable_model_error(error: ModelRuntimeError) -> bool:
    if error.code in RETRYABLE_MODEL_ERRORS:
        return True
    return error.http_status in RETRYABLE_HTTP_STATUS


def _context_json(context: dict[str, Any]) -> str:
    try:
        return json.dumps(_json_safe(context), ensure_ascii=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ToolActionClientError(
            "model_context_serialization_error",
            "model_context_serialization_error",
            retryable=True,
        ) from exc


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, set):
        return [_json_safe(item) for item in sorted(value, key=str)]
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
