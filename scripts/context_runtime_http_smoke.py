"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import argparse
import time
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import json

from bson import ObjectId
from pymongo import MongoClient

from interactions.idle_cadence import IdleCadenceService
from interactions.idle_cadence_repository import IdleRunnerStateRepository
from conversations.repository import ConversationRepository
from conversations.service import ConversationService
from diary.repository import DiaryRepository
from diary.service import DiaryService
from memory.repository import MemoryRepository
from memory.service import MemoryService
from summaries.repository import SummaryRepository
from summaries.service import SummaryService
from workers.derived_jobs import DerivedJobRepository, DerivedJobService
from workers.diary_worker import DiaryWorker
from workers.memory_worker import MemoryWorker
from workers.relationship_worker import RelationshipWorker
from workers.runner import DerivedWorkerRunner
from workers.summary_worker import SummaryWorker


def main() -> None:
    parser = argparse.ArgumentParser(description="Context Runtime V1.0 HTTP smoke")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--mongo-uri", default="mongodb://127.0.0.1:27017")
    parser.add_argument("--mongo-database", required=True)
    parser.add_argument("--expected-first-content", default=None)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    email_stamp = str(int(time.time() * 1000))
    auth = _post(
        base_url,
        "/api/users/register",
        {
            "username": f"ctxsmoke_{email_stamp[-8:]}",
            "email": f"ctxsmoke_{email_stamp}@example.com",
            "password": "password123",
        },
    )
    token = auth["accessToken"]
    user = auth["user"]
    assert user["fullPromptLoggingOn"] is True, user
    assert user["backgroundIdleOn"] is False, user

    empty_logs = _get(base_url, "/api/users/me/prompt-logs", token)
    assert empty_logs["promptLogs"] == [], empty_logs

    conversation = _post(
        base_url,
        "/api/conversations",
        {
            "mode": "idle",
            "title": "Context Runtime Smoke",
            "metadata": {"topicDirection": "验证 Context Runtime 审计包。"},
        },
        token,
    )
    first_tick = _post(
        base_url,
        f"/api/idle/{conversation['id']}/tick",
        {
            "targetAgentId": "agent_1",
            "idleSeed": "验证 context package persistence。",
            "idempotencyKey": f"first-{email_stamp}",
        },
        token,
    )
    first_retry = _post(
        base_url,
        f"/api/idle/{conversation['id']}/tick",
        {"targetAgentId": "agent_1", "idempotencyKey": f"first-{email_stamp}"},
        token,
    )
    first_package_id = first_tick["context"]["contextPackageId"]
    assert first_package_id, first_tick
    if args.expected_first_content:
        assert args.expected_first_content in first_tick["agentMessage"]["content"], first_tick
    assert first_tick["agentMessage"]["metadata"]["context_package_id"] == first_package_id
    assert first_retry["agentMessage"]["id"] == first_tick["agentMessage"]["id"], first_retry
    assert first_retry["context"]["contextPackageId"] == first_package_id, first_retry

    prompt_logs = _get(base_url, "/api/users/me/prompt-logs", token)
    assert len(prompt_logs["promptLogs"]) == 1, prompt_logs
    assert prompt_logs["promptLogs"][0]["id"] == first_package_id
    assert "Current mode: idle" in prompt_logs["promptLogs"][0]["fullPromptText"]
    assert "Relationship stance:" in prompt_logs["promptLogs"][0]["fullPromptText"]
    assert "Turn intent:" in prompt_logs["promptLogs"][0]["fullPromptText"]
    assert "Do not output stacked frameworks" in prompt_logs["promptLogs"][0]["fullPromptText"]

    updated = _patch(base_url, "/api/users/me", {"fullPromptLoggingOn": False}, token)
    assert updated["fullPromptLoggingOn"] is False, updated
    background_updated = _patch(base_url, "/api/users/me", {"backgroundIdleOn": True}, token)
    assert background_updated["backgroundIdleOn"] is True, background_updated
    second_tick = _post(
        base_url,
        f"/api/idle/{conversation['id']}/tick",
        {"targetAgentId": "agent_2", "idempotencyKey": f"second-{email_stamp}"},
        token,
    )
    second_package_id = second_tick["context"]["contextPackageId"]
    assert second_package_id and second_package_id != first_package_id, second_tick
    _post(
        base_url,
        f"/api/idle/{conversation['id']}/messages",
        {"content": "我喜欢中文简短回复。"},
        token,
    )
    companion = _post(
        base_url,
        "/api/conversations",
        {
            "mode": "companion_2",
            "title": "Memory Smoke",
        },
        token,
    )
    _post(
        base_url,
        f"/api/companion/{companion['id']}/messages",
        {"content": "I prefer concise Chinese replies.", "targetAgentId": "agent_2"},
        token,
    )

    mongo = MongoClient(args.mongo_uri)[args.mongo_database]
    cadence = IdleCadenceService(IdleRunnerStateRepository(mongo), daily_limit=1)
    disabled_decision = cadence.background_tick_decision(user=user, conversation=conversation)
    assert disabled_decision["allowed"] is False, disabled_decision
    assert disabled_decision["reason"] == "background_idle_disabled", disabled_decision
    enabled_user = {**background_updated, "id": user["id"]}
    enabled_decision = cadence.background_tick_decision(user=enabled_user, conversation=conversation)
    assert enabled_decision["allowed"] is True, enabled_decision
    cadence.record_background_tick_result(
        user_id=user["id"],
        conversation_id=conversation["id"],
        succeeded=True,
    )
    budget_decision = cadence.background_tick_decision(user=enabled_user, conversation=conversation)
    assert budget_decision["allowed"] is False, budget_decision
    assert budget_decision["reason"] == "idle_budget_exhausted", budget_decision

    packages = list(mongo["context_packages"].find({"user_id": user["id"]}).sort("created_at", 1))
    assert len(packages) == 4, packages
    assert packages[0]["full_prompt_text"], packages[0]
    assert all(row["full_prompt_text"] is None for row in packages[1:]), packages
    assert all(row["full_prompt_logging_enabled"] is False for row in packages[1:]), packages
    assert packages[1]["prompt_hash"] == second_tick["context"]["promptHash"], packages[1]

    deleted = _delete(base_url, "/api/users/me/prompt-logs", token)
    assert deleted["deletedPromptLogs"] == 1, deleted
    assert _get(base_url, "/api/users/me/prompt-logs", token)["promptLogs"] == []
    remaining = list(mongo["context_packages"].find({"user_id": user["id"]}).sort("created_at", 1))
    assert len(remaining) == 4, remaining
    assert all(row.get("full_prompt_text") is None for row in remaining), remaining

    worker_processed = _run_worker_until_current_outputs(mongo, user["id"], conversation["id"])
    assert mongo["summaries"].count_documents({"user_id": user["id"], "conversation_id": conversation["id"]}) >= 1
    relationship_memory = mongo["memory_cards"].find_one(
        {"user_id": user["id"], "scope": "idle", "memory_type": "relationship"}
    )
    assert relationship_memory is not None, relationship_memory
    assert relationship_memory["summary"] != "Nora and Vale shared another idle interaction.", relationship_memory
    assert mongo["memory_cards"].count_documents({"user_id": user["id"], "scope": "companion", "memory_type": "preference"}) >= 1
    assert mongo["diary_entries"].count_documents({"user_id": user["id"]}) >= 1
    memory_cards = _get(base_url, "/api/memory/me", token)["memoryCards"]
    assert memory_cards, memory_cards
    active_memory = next(card for card in memory_cards if card["status"] == "active")
    disabled_memory = _patch(base_url, f"/api/memory/me/{active_memory['id']}", {"status": "disabled"}, token)
    assert disabled_memory["status"] == "disabled", disabled_memory
    enabled_memory = _patch(base_url, f"/api/memory/me/{active_memory['id']}", {"status": "active"}, token)
    assert enabled_memory["status"] == "active", enabled_memory
    deleted_memory = _delete(base_url, f"/api/memory/me/{active_memory['id']}", token)
    assert deleted_memory["deletedMemoryCard"] is True, deleted_memory
    visible_after_delete = _get(base_url, "/api/memory/me", token)["memoryCards"]
    assert all(card["id"] != active_memory["id"] for card in visible_after_delete), visible_after_delete
    for index in range(22):
        _post(
            base_url,
            f"/api/conversations/{conversation['id']}/messages",
            {
                "sender_type": "agent",
                "sender_slot": "agent_1" if index % 2 == 0 else "agent_2",
                "role": "assistant",
                "content": f"summary selection filler {index}",
            },
            token,
        )
    summary_tick = _post(
        base_url,
        f"/api/idle/{conversation['id']}/tick",
        {"targetAgentId": "agent_1", "idempotencyKey": f"summary-{email_stamp}"},
        token,
    )
    summary_package = _find_by_id(mongo["context_packages"], summary_tick["context"]["contextPackageId"])
    assert summary_package is not None, summary_tick
    included_summary_ids = summary_package.get("included_summary_ids") or []
    assert included_summary_ids, summary_package
    assert not included_summary_ids[0].startswith("compact-"), summary_package

    print(
        "context_runtime_http_smoke=ok "
        f"user={user['id']} "
        f"conversation={conversation['id']} "
        f"packages={len(remaining) + 1} "
        f"first={first_package_id} "
        f"second={second_package_id} "
        "idempotent_retry=ok "
        "background_gate=ok "
        "memory_controls=ok "
        f"worker_processed={worker_processed} "
        f"persisted_summary={included_summary_ids[0]}"
    )


def _get(base_url: str, path: str, token: str | None = None) -> dict[str, Any]:
    return _request(base_url, path, "GET", None, token)


def _post(base_url: str, path: str, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    return _request(base_url, path, "POST", payload, token)


def _patch(base_url: str, path: str, payload: dict[str, Any], token: str | None = None) -> dict[str, Any]:
    return _request(base_url, path, "PATCH", payload, token)


def _delete(base_url: str, path: str, token: str | None = None) -> dict[str, Any]:
    return _request(base_url, path, "DELETE", None, token)


def _request(
    base_url: str,
    path: str,
    method: str,
    payload: dict[str, Any] | None,
    token: str | None,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 HacksonSmoke/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{base_url}{path}", data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        raise AssertionError(f"{method} {path} failed: {exc.code} {error_body}") from exc
    return json.loads(raw) if raw else {}


def _run_worker_until_current_outputs(mongo, user_id: str, conversation_id: str) -> int:
    conversation_service = ConversationService(ConversationRepository(mongo))
    summary_service = SummaryService(SummaryRepository(mongo))
    memory_service = MemoryService(MemoryRepository(mongo))
    diary_service = DiaryService(DiaryRepository(mongo))
    job_service = DerivedJobService(DerivedJobRepository(mongo))
    runner = DerivedWorkerRunner(
        job_service,
        SummaryWorker(conversation_service, summary_service),
        MemoryWorker(conversation_service, memory_service),
        DiaryWorker(diary_service),
        RelationshipWorker(conversation_service, memory_service),
    )
    processed = 0
    for _ in range(10):
        processed += runner.run_once(limit=100, user_id=user_id)
        if (
            mongo["summaries"].count_documents({"user_id": user_id, "conversation_id": conversation_id}) >= 1
            and mongo["memory_cards"].count_documents(
                {"user_id": user_id, "scope": "idle", "memory_type": "relationship"}
            )
            >= 1
            and mongo["memory_cards"].count_documents(
                {"user_id": user_id, "scope": "companion", "memory_type": "preference"}
            )
            >= 1
            and mongo["diary_entries"].count_documents({"user_id": user_id}) >= 1
        ):
            return processed
        if processed == 0:
            break
    return processed


def _find_by_id(collection, document_id: str) -> dict[str, Any] | None:
    try:
        object_id = ObjectId(document_id)
    except Exception:
        object_id = document_id
    return collection.find_one({"_id": object_id})


if __name__ == "__main__":
    main()
