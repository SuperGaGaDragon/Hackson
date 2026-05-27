"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any


def public_project(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Project document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "name": document["name"],
        "repoPath": document["repo_path"],
        "status": document["status"],
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_mission(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Mission document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "projectId": _public_id(document["project_id"]),
        "title": document["title"],
        "goal": document["goal"],
        "status": document["status"],
        "autonomyLevel": document.get("autonomy_level", "supervised"),
        "maxIterations": document.get("max_iterations", 1),
        "leadEmployeeId": document.get("lead_employee_id", "employee_default_lead"),
        "leadEmployeeName": document.get("lead_employee_name", "Lead"),
        "leadEmployeeRole": document.get("lead_employee_role", "Mission lead"),
        "supportingEmployeeIds": document.get("supporting_employee_ids", []),
        "currentStep": document.get("current_step"),
        "lastError": document.get("last_error"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_employee(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Employee document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "name": document["name"],
        "role": document["role"],
        "personality": document.get("personality", ""),
        "experience": document.get("experience", []),
        "skills": document.get("skills", []),
        "permissions": document.get("permissions", {}),
        "defaultOutputStyle": document.get("default_output_style", "structured_summary"),
        "status": document.get("status", "active"),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_project_employee(document: dict[str, Any], employee: dict[str, Any]) -> dict[str, Any]:
    """Convert a Project Employee membership to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "projectId": _public_id(document["project_id"]),
        "employeeId": _public_id(document["employee_id"]),
        "employee": public_employee(employee),
        "roleOnProject": document.get("role_on_project", "Member"),
        "isLeadDefault": bool(document.get("is_lead_default", False)),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_run(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Run document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "status": document["status"],
        "iteration": document.get("iteration", 1),
        "startedAt": document["started_at"],
        "endedAt": document.get("ended_at"),
        "metadata": document.get("metadata", {}),
    }


def public_step(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Step document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "runId": _public_id(document["run_id"]),
        "sequence": document["sequence"],
        "title": document["title"],
        "status": document["status"],
        "startedAt": document.get("started_at"),
        "endedAt": document.get("ended_at"),
        "metadata": document.get("metadata", {}),
    }


def public_artifact(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Artifact document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "runId": _public_id(document["run_id"]),
        "kind": document["kind"],
        "title": document["title"],
        "content": document["content"],
        "createdByEmployee": document.get("created_by_employee", {}),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
    }


def public_product(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Product document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "title": document["title"],
        "summary": document.get("summary", ""),
        "status": document.get("status", "active"),
        "artifactIds": [_public_id(value) for value in document.get("artifact_ids", [])],
        "latestArtifactId": _public_id(document.get("latest_artifact_id")) if document.get("latest_artifact_id") else None,
        "createdBy": document.get("created_by", {}),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_work_window(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Work Window document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "runId": _public_id(document["run_id"]) if document.get("run_id") else None,
        "agentSlot": document["agent_slot"],
        "title": document["title"],
        "brief": document["brief"],
        "status": document["status"],
        "resultArtifactId": _public_id(document.get("result_artifact_id")) if document.get("result_artifact_id") else None,
        "summary": document.get("summary", ""),
        "metadata": document.get("metadata", {}),
        "createdAt": document["created_at"],
        "updatedAt": document["updated_at"],
    }


def public_event(document: dict[str, Any]) -> dict[str, Any]:
    """Convert a persisted Event document to the public API shape."""
    return {
        "id": _public_id(document["_id"]),
        "userId": document["user_id"],
        "missionId": _public_id(document["mission_id"]),
        "runId": _public_id(document.get("run_id")) if document.get("run_id") is not None else None,
        "stepId": _public_id(document.get("step_id")) if document.get("step_id") is not None else None,
        "sequence": document["sequence"],
        "type": document["type"],
        "title": document["title"],
        "message": document["message"],
        "payload": document.get("payload", {}),
        "createdAt": document["created_at"],
    }


def _public_id(value: Any) -> str:
    return str(value)
