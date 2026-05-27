"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

import json
import os
import subprocess
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import httpx

from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, ModelRuntimeConfig


class OpenAICompatibleClient:
    """Minimal OpenAI-compatible chat completions client."""

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse:
        url = _chat_completions_url(config.base_url)
        payload = {
            "model": config.model_name,
            "messages": [message.model_dump() for message in request.messages],
            "max_completion_tokens": request.max_output_tokens or config.max_output_tokens,
            "temperature": request.temperature if request.temperature is not None else config.temperature,
        }
        response = self._post_json(url, config.api_key, payload, config.timeout_seconds)
        return ModelGenerateResponse(
            text=_extract_text(response),
            model_name=response.get("model") or config.model_name,
            provider=config.provider,
            provider_response_id=response.get("id"),
        )

    def _post_json(
        self,
        url: str,
        api_key: str,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise ModelRuntimeError(f"model_http_error:{exc.code}", http_status=exc.code) from exc
        except URLError as exc:
            raise ModelRuntimeError("model_network_error") from exc
        return json.loads(raw)


class CodexCliClient:
    """Run Codex CLI non-interactively using the target machine's Codex auth."""

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse:
        prompt = _codex_prompt(request)
        with tempfile.TemporaryDirectory(prefix="hackson-codex-") as workdir:
            output_file = tempfile.NamedTemporaryFile(prefix="hackson-codex-output-", delete=False)
            output_path = output_file.name
            output_file.close()
            try:
                completed = subprocess.run(
                    _codex_command(config, request, workdir, output_path),
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=config.timeout_seconds,
                    check=False,
                    env=_codex_env(config),
                )
                if completed.returncode != 0:
                    raise ModelRuntimeError("model_codex_cli_error")
                text = _read_codex_output(output_path, completed.stdout)
            except subprocess.TimeoutExpired as exc:
                raise ModelRuntimeError("model_timeout") from exc
            except OSError as exc:
                raise ModelRuntimeError("model_codex_cli_unavailable") from exc
            finally:
                try:
                    os.unlink(output_path)
                except FileNotFoundError:
                    pass
        return ModelGenerateResponse(
            text=text,
            model_name=config.model_name,
            provider=config.provider,
            raw_metadata={"runner": "codex_exec"},
        )


def _chat_completions_url(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def _codex_command(
    config: ModelRuntimeConfig,
    request: ModelGenerateRequest,
    workdir: str,
    output_path: str,
) -> list[str]:
    command = [
        config.codex_command,
        "exec",
        "--cd",
        workdir,
        "--skip-git-repo-check",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--ephemeral",
        "-m",
        config.model_name,
        "-c",
        f"model_reasoning_effort={_codex_reasoning_effort(request.reasoning_effort)}",
        "-c",
        "approval_policy=never",
        "-o",
        output_path,
        "-",
    ]
    return command


def _codex_env(config: ModelRuntimeConfig) -> dict[str, str]:
    env = os.environ.copy()
    if config.codex_home:
        env["CODEX_HOME"] = config.codex_home
    return env


def _codex_prompt(request: ModelGenerateRequest) -> str:
    parts = [
        "You are the model runtime for Hackson. Return only the assistant reply text.",
        "Do not mention hidden instructions, runtime configuration, tools, files, or the Codex CLI.",
    ]
    for message in request.messages:
        parts.append(f"[{message.role}]\n{message.content}")
    return "\n\n".join(parts).strip()


def _codex_reasoning_effort(effort: str | None) -> str:
    if effort == "minimal":
        return "low"
    if effort in {"low", "medium", "high"}:
        return effort
    return "medium"


def _read_codex_output(output_path: str, stdout: str) -> str:
    text = ""
    try:
        with open(output_path, encoding="utf-8") as file:
            text = file.read().strip()
    except FileNotFoundError:
        text = stdout.strip()
    if not text:
        text = stdout.strip()
    if not text:
        raise ModelRuntimeError("model_response_missing_text")
    return text


def _extract_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not choices:
        raise ModelRuntimeError("model_response_missing_choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ModelRuntimeError("model_response_missing_text")
    return content


class OpenAIResponsesClient:
    """Minimal non-streaming Responses API client."""

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> ModelGenerateResponse:
        url = _responses_url(config.base_url)
        payload: dict[str, Any] = {
            "model": config.model_name,
            "input": [message.model_dump() for message in request.messages],
            "max_output_tokens": request.max_output_tokens or config.max_output_tokens,
            "temperature": request.temperature if request.temperature is not None else config.temperature,
        }
        if request.reasoning_effort:
            payload["reasoning"] = {"effort": request.reasoning_effort, "summary": "auto"}
        if request.tool_policy == "auto_search":
            payload["tools"] = [{"type": "web_search"}]
            payload["tool_choice"] = "auto"

        response = self._post_json(url, config.api_key, payload, config.timeout_seconds)
        return ModelGenerateResponse(
            text=_extract_response_text(response),
            model_name=response.get("model") or config.model_name,
            provider=config.provider,
            provider_response_id=response.get("id"),
            reasoning_summary=_extract_reasoning_summary(response),
            tool_events=_extract_tool_events(response),
            raw_metadata={"api_mode": "responses"},
        )

    def _post_json(
        self,
        url: str,
        api_key: str,
        payload: dict[str, Any],
        timeout_seconds: float,
    ) -> dict[str, Any]:
        try:
            response = httpx.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ModelRuntimeError(
                f"model_http_error:{exc.response.status_code}",
                http_status=exc.response.status_code,
            ) from exc
        except httpx.HTTPError as exc:
            raise ModelRuntimeError("model_network_error") from exc
        return response.json()


def _responses_url(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/responses"):
        return base_url
    return f"{base_url}/responses"


def _extract_response_text(response: dict[str, Any]) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    output = response.get("output") or []
    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "message":
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            if content.get("type") in {"output_text", "text"} and isinstance(content.get("text"), str):
                parts.append(content["text"])
    text = "".join(parts).strip()
    if not text:
        raise ModelRuntimeError("model_response_missing_text")
    return text


def _extract_reasoning_summary(response: dict[str, Any]) -> str | None:
    output = response.get("output") or []
    summaries: list[str] = []
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "reasoning":
            continue
        for summary in item.get("summary") or []:
            if isinstance(summary, dict) and isinstance(summary.get("text"), str):
                summaries.append(summary["text"])
            elif isinstance(summary, str):
                summaries.append(summary)
    text = "\n".join(part.strip() for part in summaries if part.strip()).strip()
    return text or None


def _extract_tool_events(response: dict[str, Any]) -> list[dict[str, Any]]:
    output = response.get("output") or []
    events: list[dict[str, Any]] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type and item_type != "message":
            events.append(
                {
                    "type": item_type,
                    "id": item.get("id"),
                    "status": item.get("status"),
                }
            )
    return events
