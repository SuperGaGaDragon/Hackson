"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any

from work_mode.tool_protocol import ToolName

AVAILABLE_V1_TOOLS: tuple[ToolName, ...] = (
    "mission_plan",
    "work_product",
    "inspect_product",
    "delegate_agent",
    "ask_user",
    "finish_mission",
    "block_mission",
)


def build_lead_context(
    mission: dict[str, Any],
    lead_agent: dict[str, Any],
    delegate_agent: dict[str, Any],
    products: list[dict[str, Any]],
    work_windows: list[dict[str, Any]],
    events: list[dict[str, Any]],
    artifacts: list[dict[str, Any]],
    last_observation: dict[str, Any] | None,
    budget: dict[str, Any],
    recent_artifact_limit: int = 2,
    recent_event_limit: int = 20,
) -> dict[str, Any]:
    """Build the bounded state package shown to the Lead Agent."""
    return {
        "mission": _mission_context(mission),
        "leadAgent": lead_agent,
        "delegateAgent": delegate_agent,
        "availableTools": list(AVAILABLE_V1_TOOLS),
        "hardConstraints": [
            "Return exactly one tool action.",
            "Do not return plain assistant text.",
            "Do not create new tools.",
            "Do not emit React components.",
            "Do not use shell, file, browser, or computer-control tools.",
        ],
        "productManifest": [_product_manifest(product) for product in products],
        "workWindowManifest": [_window_manifest(window) for window in work_windows],
        "recentEvents": [_event_context(event) for event in events[-recent_event_limit:]],
        "recentArtifactContent": [
            _artifact_context(artifact)
            for artifact in artifacts[-max(recent_artifact_limit, 0) :]
            if recent_artifact_limit > 0
        ],
        "lastObservation": last_observation or {},
        "budget": budget,
    }


def build_delegate_context(
    mission: dict[str, Any],
    delegate_agent: dict[str, Any],
    brief: str,
    expected_output: str,
    target_product: dict[str, Any] | None,
    source_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the scoped one-shot context shown to a Delegate Agent."""
    return {
        "mission": _mission_context(mission),
        "delegateAgent": delegate_agent,
        "brief": brief,
        "expectedOutput": expected_output,
        "targetProduct": _product_manifest(target_product) if target_product else None,
        "sourceArtifacts": [_artifact_context(artifact) for artifact in source_artifacts],
        "responseContract": (
            "You must return structured delegate result JSON with status, title, summary, content, and reason. "
            "You cannot call tools or finish the mission."
        ),
    }


def _mission_context(mission: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": mission["id"],
        "title": mission["title"],
        "goal": mission["goal"],
        "status": mission.get("status", "running"),
    }


def _product_manifest(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": product["id"],
        "title": product["title"],
        "status": product.get("status", "active"),
        "summary": product.get("summary", ""),
        "artifactIds": product.get("artifactIds", []),
        "latestArtifactId": product.get("latestArtifactId"),
    }


def _window_manifest(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": window["id"],
        "agentSlot": window["agentSlot"],
        "title": window["title"],
        "status": window["status"],
        "resultArtifactId": window.get("resultArtifactId"),
        "summary": window.get("summary", ""),
    }


def _event_context(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "sequence": event["sequence"],
        "type": event["type"],
        "title": event["title"],
        "message": event["message"],
        "payload": event.get("payload", {}),
    }


def _artifact_context(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": artifact["id"],
        "title": artifact["title"],
        "kind": artifact.get("kind", "other"),
        "summary": artifact.get("summary") or artifact.get("metadata", {}).get("summary", ""),
        "content": artifact.get("content", ""),
        "metadata": artifact.get("metadata", {}),
    }
