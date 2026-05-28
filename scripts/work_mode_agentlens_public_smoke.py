"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from urllib import error, request
from uuid import uuid4

import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from core.config import get_settings
from core.database import close_mongo, connect_mongo, get_database
from work_mode.repository import WorkModeRepository
from work_mode.schemas import MissionStartRequest
from work_mode.service import WorkModeService

BASE_URL = os.environ.get("HACKSON_PUBLIC_URL", "https://hackson.catachess.com").rstrip("/")


def main() -> None:
    user = f"agentlens{uuid4().hex[:8]}"
    password = f"agentlens-{uuid4().hex[:16]}"
    token = _register(user, password)
    headers = {"Authorization": f"Bearer {token}"}
    project = _post("/api/work/projects", {"name": "AgentLens Public Smoke"}, headers, 201)
    mission = _post(
        "/api/work/missions",
        {
            "projectId": project["id"],
            "title": "AgentLens Toronto AI reliability smoke",
            "goal": (
                "Find 3 AI startups in Toronto working on enterprise AI. "
                "For each, give one-sentence summary, source link, and personalized outreach email."
            ),
        },
        headers,
        201,
    )
    seeded = _seed_completed_trace(user_id=_me(headers)["id"], mission_id=mission["id"])
    evaluated = _post(f"/api/work/missions/{mission['id']}/evaluate", {}, headers, 200)
    report = _report_payload(evaluated)
    event_types = [event["type"] for event in evaluated["events"]]
    issue_types = {issue["type"] for issue in report["issues"]}

    assert "RELIABILITY_REPORTED" in event_types, "missing_reliability_reported"
    assert report["reportArtifactId"], "missing_report_artifact_id"
    assert "unsupported_claim" in issue_types, f"missing_unsupported_claim:{issue_types}"
    assert "hallucinated_entity" in issue_types, f"missing_hallucinated_entity:{issue_types}"
    assert "tool_failure_ignored" in issue_types, f"missing_tool_failure_ignored:{issue_types}"
    assert report["score"] < 85, f"score_should_need_review:{report['score']}"

    print(
        "work_mode_agentlens_public_smoke=ok "
        f"base={BASE_URL} "
        f"mission={mission['id']} "
        f"run={seeded['runId']} "
        f"score={report['score']} "
        f"status={report['status']} "
        f"issues={','.join(sorted(issue_types))}"
    )
    _write_state(
        {
            "baseUrl": BASE_URL,
            "username": user,
            "accessToken": token,
            "projectId": project["id"],
            "missionId": mission["id"],
            "runId": seeded["runId"],
            "score": report["score"],
            "status": report["status"],
            "issues": sorted(issue_types),
        }
    )


def _register(username: str, password: str) -> str:
    response = _request(
        "POST",
        "/api/users/register",
        {"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert response["status"] == 201, response["body"]
    return response["json"]["accessToken"]


def _me(headers: dict[str, str]) -> dict:
    response = _request("GET", "/api/users/me", headers=headers)
    assert response["status"] == 200, response["body"]
    return response["json"]


def _post(path: str, payload: dict, headers: dict[str, str], expected_status: int) -> dict:
    response = _request("POST", path, payload, headers)
    assert response["status"] == expected_status, response["body"]
    return response["json"]


def _request(method: str, path: str, payload: dict | None = None, headers: dict[str, str] | None = None) -> dict:
    body = json.dumps(payload or {}).encode("utf-8") if method != "GET" else None
    req = request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 AgentLensPublicSmoke/1.0",
            **(headers or {}),
        },
        method=method,
    )
    try:
        with request.urlopen(req, timeout=20) as response:
            text = response.read().decode("utf-8")
            return {"status": response.status, "body": text, "json": json.loads(text)}
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        try:
            parsed = json.loads(text) if text else {}
        except json.JSONDecodeError:
            parsed = {}
        return {"status": exc.code, "body": text, "json": parsed}


def _seed_completed_trace(user_id: str, mission_id: str) -> dict[str, str]:
    connect_mongo()
    try:
        service = WorkModeService(WorkModeRepository(get_database()))
        detail = service.start_mission(user_id, mission_id, MissionStartRequest(metadata={"smoke": "agentlens"}))
        run_id = detail["activeRun"]["id"]
        product = service.create_product(
            user_id,
            mission_id,
            title="Toronto AI outreach",
            summary="Seeded public AgentLens smoke result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
            metadata={"smoke": "agentlens"},
        )
        artifact = service.create_product_artifact(
            user_id,
            mission_id,
            run_id,
            product["id"],
            kind="final",
            title="Seeded Toronto AI research",
            content=(
                "Cohere is a Toronto-based enterprise AI company. Source: https://cohere.com\n"
                "MapleNeural Labs provides enterprise AI agents to Fortune 500 banks.\n"
                "Email: Dear team, I liked your enterprise AI work."
            ),
            summary="Seeded public AgentLens smoke result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
            source_artifact_ids=[],
            work_window_id=None,
            metadata={"summary": "Seeded public AgentLens smoke result.", "smoke": "agentlens"},
        )
        mission_document = service._require_mission(user_id, mission_id)
        service.append_event(
            user_id,
            mission_document,
            run={"_id": run_id},
            step=None,
            event_type="WEB_SEARCH_COMPLETED",
            title="Search",
            message="Toronto enterprise AI startups",
            payload={
                "tool": "web_search",
                "status": "ok",
                "query": "Toronto enterprise AI startups",
                "provider": "seeded_public_smoke",
                "results": [
                    {
                        "title": "Cohere enterprise AI",
                        "url": "https://cohere.com",
                        "source": "cohere.com",
                        "snippet": "Cohere provides enterprise AI models and is headquartered in Toronto.",
                        "publishedAt": None,
                    }
                ],
            },
        )
        service.append_event(
            user_id,
            mission_document,
            run={"_id": run_id},
            step=None,
            event_type="WEB_SEARCH_FAILED",
            title="Search failed",
            message="search_timeout",
            payload={"tool": "web_search", "status": "failed", "code": "search_timeout"},
        )
        service.mark_product_final(user_id, product["id"])
        service.mark_mission_completed(
            user_id,
            mission_id,
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[artifact["id"]],
            summary="Seeded AgentLens public smoke completed.",
        )
        return {"runId": run_id, "artifactId": artifact["id"]}
    finally:
        close_mongo()


def _report_payload(detail: dict) -> dict:
    reports = [
        artifact
        for artifact in detail["artifacts"]
        if artifact.get("metadata", {}).get("artifactRole") == "reliability_report"
    ]
    assert reports, "missing_report_artifact"
    report = reports[0]["metadata"].get("reportPayload")
    assert isinstance(report, dict), "missing_report_payload"
    assert report.get("reportArtifactId") == reports[0]["id"], "report_artifact_id_mismatch"
    return report


def _write_state(state: dict) -> None:
    output_path = os.environ.get("HACKSON_AGENTLENS_PUBLIC_SMOKE_STATE")
    if not output_path:
        return
    Path(output_path).write_text(json.dumps(state), encoding="utf-8")


if __name__ == "__main__":
    main()
