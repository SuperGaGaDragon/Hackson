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
        "toolActionEnvelope": {"tool": "one available tool name", "arguments": "object matching toolSchemas[tool]"},
        "toolSchemas": _tool_schemas(),
        "toolExamples": _tool_examples(),
        "hardConstraints": [
            "Return exactly one tool action.",
            "Return valid JSON only, with top-level tool and arguments.",
            "Do not return plain assistant text.",
            "Do not create new tools.",
            "Do not emit React components.",
            "Do not use shell, file, browser, or computer-control tools.",
            "For long writing goals, split work into Product Artifacts and Delegate windows instead of trying to finish all content in one Lead turn.",
            "Use work_product whenever you need to show or persist natural-language output.",
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


def _tool_schemas() -> dict[str, Any]:
    return {
        "mission_plan": {
            "arguments": {
                "reason": "string <=240",
                "planTitle": "string",
                "steps": [{"title": "string", "status": "pending|in_progress|completed|changed", "notes": "string"}],
            }
        },
        "work_product": {
            "arguments": {
                "reason": "string <=240",
                "operation": "create_product|append_artifact|revise_artifact|finalize_product",
                "productId": "string|null; null only for create_product",
                "sourceArtifactIds": ["artifact id strings"],
                "productTitle": "string",
                "artifactTitle": "string",
                "artifactKind": "outline|chapter|draft|revision|final|report|notes|other",
                "content": "string",
                "summary": "string",
            }
        },
        "inspect_product": {
            "arguments": {
                "reason": "string <=240",
                "productIds": ["product id strings"],
                "artifactIds": ["artifact id strings"],
                "focus": "string",
            }
        },
        "delegate_agent": {
            "arguments": {
                "reason": "string <=240",
                "agentSlot": "non-lead agent_1 or agent_2",
                "windowTitle": "string",
                "brief": "string",
                "expectedOutput": "outline|chapter|review|revision|summary|other",
                "targetProductId": "string|null",
                "sourceArtifactIds": ["artifact id strings"],
            }
        },
        "ask_user": {
            "arguments": {"reason": "string <=240", "question": "string", "suggestedOptions": ["strings"]}
        },
        "finish_mission": {
            "arguments": {
                "reason": "string <=240",
                "summary": "string",
                "finalProductIds": ["existing product id strings"],
                "finalArtifactIds": ["existing artifact id strings"],
            }
        },
        "block_mission": {
            "arguments": {"reason": "string <=240", "blockedReason": "string", "neededFromUser": "string"}
        },
    }


def _tool_examples() -> dict[str, Any]:
    return {
        "missionPlanExample": {
            "tool": "mission_plan",
            "arguments": {
                "reason": "先规划任务。",
                "planTitle": "执行计划",
                "steps": [{"title": "创建产品", "status": "pending", "notes": ""}],
            },
        },
        "workProductExample": {
            "tool": "work_product",
            "arguments": {
                "reason": "创建第一版产品。",
                "operation": "create_product",
                "productId": None,
                "sourceArtifactIds": [],
                "productTitle": "长篇小说",
                "artifactTitle": "故事大纲",
                "artifactKind": "outline",
                "content": "正文内容",
                "summary": "完成大纲。",
            },
        },
        "finishMissionExample": {
            "tool": "finish_mission",
            "arguments": {
                "reason": "最终产品已完成。",
                "summary": "任务完成。",
                "finalProductIds": ["product_id_from_productManifest"],
                "finalArtifactIds": ["latestArtifactId_from_productManifest"],
            },
        },
    }
