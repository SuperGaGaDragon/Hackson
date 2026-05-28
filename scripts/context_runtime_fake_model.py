"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI


app = FastAPI(title="Hackson Context Runtime Fake Model")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat_completions(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deterministic assistant message for target-machine smoke."""
    messages = payload.get("messages") or []
    prompt = "\n".join(str(message.get("content", "")) for message in messages if isinstance(message, dict))
    if "companion_1" in prompt:
        text = "我看到你加入了，我们刚才在把 idle 话题转向你。"
    elif "companion_2" in prompt:
        text = "Hackson 的 V1 重点是可审计上下文和稳定对话。"
    elif "Relationship stance:" in prompt and "Turn intent:" in prompt:
        text = "我先接你刚才那句，不急着把它做成方法论。"
    else:
        text = "那我们继续把这个 idle 话题讲清楚。"
    return {
        "id": "fake-context-runtime-response",
        "object": "chat.completion",
        "model": payload.get("model") or "fake-context-runtime-model",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": text},
            }
        ],
    }
