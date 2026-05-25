"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from model_runtime.schemas import ModelGenerateRequest, ModelRuntimeConfig


class OpenAICompatibleClient:
    """Minimal OpenAI-compatible chat completions client."""

    def generate(self, config: ModelRuntimeConfig, request: ModelGenerateRequest) -> str:
        url = _chat_completions_url(config.base_url)
        payload = {
            "model": config.model_name,
            "messages": [message.model_dump() for message in request.messages],
            "max_completion_tokens": request.max_output_tokens or config.max_output_tokens,
            "temperature": request.temperature if request.temperature is not None else config.temperature,
        }
        response = self._post_json(url, config.api_key, payload, config.timeout_seconds)
        return _extract_text(response)

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
            raise RuntimeError(f"model_http_error:{exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("model_network_error") from exc
        return json.loads(raw)


def _chat_completions_url(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def _extract_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not choices:
        raise RuntimeError("model_response_missing_choices")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("model_response_missing_text")
    return content
