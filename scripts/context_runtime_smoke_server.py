"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Context Runtime UI Smoke Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_ID = "smoke_user"
messages: list[dict[str, Any]] = []
conversation: dict[str, Any]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/users/register")
def register(payload: dict[str, Any]) -> dict[str, Any]:
    return {"accessToken": "smoke-token", "tokenType": "bearer", "user": _user(payload.get("username") or "smoke")}


@app.post("/api/users/login")
def login(payload: dict[str, Any]) -> dict[str, Any]:
    return {"accessToken": "smoke-token", "tokenType": "bearer", "user": _user("smoke")}


@app.get("/api/users/me")
def me() -> dict[str, Any]:
    return _user("smoke")


@app.patch("/api/users/me")
def update_me(payload: dict[str, Any]) -> dict[str, Any]:
    return {**_user("smoke"), **payload}


@app.get("/api/users/me/prompt-logs")
def prompt_logs() -> dict[str, list]:
    return {"promptLogs": []}


@app.get("/api/memory/me")
def memory() -> dict[str, list]:
    return {"memoryCards": []}


@app.get("/api/agents")
def agents() -> list[dict[str, Any]]:
    return _user("smoke")["agentProfiles"]


@app.get("/api/conversations")
def list_conversations(mode: str | None = None) -> list[dict[str, Any]]:
    return [conversation] if mode in (None, "idle") else []


@app.post("/api/conversations")
def create_conversation(payload: dict[str, Any]) -> dict[str, Any]:
    global conversation, messages
    messages = []
    conversation = _conversation(title=payload.get("title") or "Idle", metadata=payload.get("metadata") or {})
    return conversation


@app.get("/api/idle/conversation")
def idle_conversation() -> dict[str, Any]:
    return conversation


@app.get("/api/conversations/{conversation_id}/messages")
def list_messages(conversation_id: str) -> dict[str, Any]:
    return {"messages": messages, "nextAfterSequence": None}


@app.post("/api/idle/{conversation_id}/tick")
def tick(conversation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    time.sleep(1.2)
    agent = _append_message("agent", "agent_1", "Nora", "我先接 Vale 那句，不急着给结论。")
    return _interaction(agent_message=agent)


@app.post("/api/idle/{conversation_id}/messages")
def idle_message(conversation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    user = _append_message("user", None, "You", payload["content"])
    agent = _append_message("agent", "agent_2", "Vale", "你这个插话更像是在把问题拉回人身上。")
    return _interaction(user_message=user, agent_message=agent)


@app.post("/api/idle/{conversation_id}/join")
def join(conversation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    user = _append_message("user", None, "You", payload["content"])
    agent = _append_message("agent", "agent_1", "Nora", "你加入得刚好。")
    return _interaction(user_message=user, agent_message=agent)


@app.post("/api/companion/{conversation_id}/messages")
def companion_message(conversation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    user = _append_message("user", None, "You", payload["content"])
    agent = _append_message("agent", "agent_1", "Nora", "我接着你说。")
    return _interaction(user_message=user, agent_message=agent)


def _conversation(title: str = "Idle", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": "idle_smoke",
        "userId": USER_ID,
        "mode": "idle",
        "status": "active",
        "title": title,
        "participantSlots": ["agent_1", "agent_2"],
        "parentConversationId": None,
        "messageCount": len(messages) if "messages" in globals() else 0,
        "lastMessageAt": None,
        "metadata": metadata or {"topicDirection": "聊得像人一点。"},
        "createdAt": "2026-05-28T00:00:00Z",
        "updatedAt": "2026-05-28T00:00:00Z",
    }


def _user(username: str) -> dict[str, Any]:
    return {
        "id": USER_ID,
        "username": username,
        "displayName": username,
        "email": f"{username}@example.com",
        "idleOn": True,
        "backgroundIdleOn": False,
        "fullPromptLoggingOn": True,
        "languagePreference": "zh",
        "personality": "",
        "story": "",
        "agentProfiles": [
            {
                "slot": "agent_1",
                "name": "Nora",
                "short": "A1",
                "color": "teal",
                "voice": "precise",
                "personality": "会追问但不急着总结。",
                "story": "",
            },
            {
                "slot": "agent_2",
                "name": "Vale",
                "short": "A2",
                "color": "amber",
                "voice": "direct",
                "personality": "直接但会接住对方。",
                "story": "",
            },
        ],
        "createdAt": "2026-05-28T00:00:00Z",
        "updatedAt": "2026-05-28T00:00:00Z",
    }


def _append_message(sender_type: str, sender_slot: str | None, sender_name: str, content: str) -> dict[str, Any]:
    message = {
        "id": f"message_{len(messages) + 1}",
        "conversationId": conversation["id"],
        "userId": USER_ID,
        "mode": "idle",
        "sequence": len(messages) + 1,
        "senderType": sender_type,
        "senderId": USER_ID if sender_type == "user" else None,
        "senderSlot": sender_slot,
        "role": "user" if sender_type == "user" else "assistant",
        "content": content,
        "contentType": "text",
        "metadata": {},
        "createdAt": "2026-05-28T00:00:00Z",
    }
    messages.append(message)
    conversation["messageCount"] = len(messages)
    return message


def _interaction(agent_message: dict[str, Any], user_message: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "conversation": conversation,
        "userMessage": user_message,
        "agentMessage": agent_message,
        "context": {
            "promptHash": "smoke",
            "contextPackageId": "context_package_smoke",
            "tokenEstimate": 100,
            "modelName": "smoke",
            "orchestrationPolicy": "idle_quality_v1",
            "reasoningEffort": "low",
        },
    }


conversation = _conversation()
