"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any


def public_task(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a task persistence document to the public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "conversationId": document["conversation_id"],
        "objective": document["objective"],
        "status": document["status"],
        "currentPhase": document.get("current_phase"),
        "planSummary": document.get("plan_summary"),
        "progressSummary": document.get("progress_summary"),
        "openQuestions": document.get("open_questions", []),
        "blockers": document.get("blockers", []),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_tool_trace(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a tool trace persistence document to the public API shape."""
    return {
        "id": str(document["_id"]),
        "userId": document["user_id"],
        "taskId": document["task_id"],
        "conversationId": document["conversation_id"],
        "toolName": document["tool_name"],
        "inputSummary": document["input_summary"],
        "outputSummary": document.get("output_summary"),
        "status": document["status"],
        "createdAt": document["created_at"],
    }
