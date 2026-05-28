"""
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from users.auth import get_current_user_id
from work_mode.loop import MissionLoopRunner
from work_mode.routes import (
    _mission_event_stream,
    get_evaluator_runtime,
    get_user_service,
    get_work_mode_service,
    get_work_mode_worker_launcher,
    router,
)
from work_mode.evaluator import EvaluatorRuntime
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_protocol import parse_tool_action

TEST_USER_ID = "work_route_user"


class FakeUserService:
    def get_user(self, user_id: str) -> dict:
        return {
            "id": user_id,
            "agentProfiles": [
                {
                    "slot": "agent_1",
                    "name": "Planner",
                    "short": "A1",
                    "color": "teal",
                    "voice": "careful planner",
                    "personality": "Plans missions before execution.",
                    "story": "",
                },
                {
                    "slot": "agent_2",
                    "name": "Writer",
                    "short": "A2",
                    "color": "amber",
                    "voice": "direct writer",
                    "personality": "Writes concise drafts.",
                    "story": "",
                },
            ],
        }


class ScriptedRouteActionClient:
    def __init__(self) -> None:
        self.calls = 0
        self.product_id: str | None = None
        self.artifact_id: str | None = None

    def generate_action(self, context: dict):
        self.calls += 1
        products = context.get("productManifest") or []
        if products:
            self.product_id = products[0]["id"]
            self.artifact_id = products[0]["latestArtifactId"]
        if self.calls == 1:
            return parse_tool_action(
                """
                {
                  "tool": "mission_plan",
                  "arguments": {
                    "reason": "先规划。",
                    "planTitle": "Route plan",
                    "steps": [{"title": "写正文", "status": "pending", "notes": ""}]
                  }
                }
                """
            )
        if self.calls == 2:
            return parse_tool_action(
                """
                {
                  "tool": "work_product",
                  "arguments": {
                    "reason": "写入产品。",
                    "operation": "create_product",
                    "productId": null,
                    "sourceArtifactIds": [],
                    "productTitle": "Route product",
                    "artifactTitle": "Route artifact",
                    "artifactKind": "draft",
                    "content": "Route generated artifact.",
                    "summary": "Route generated artifact."
                  }
                }
                """
            )
        return parse_tool_action(
            f"""
            {{
              "tool": "finish_mission",
              "arguments": {{
                "reason": "产品已完成。",
                "summary": "Route mission complete.",
                "finalProductIds": ["{self.product_id}"],
                "finalArtifactIds": ["{self.artifact_id}"]
              }}
            }}
            """
        )


class AskThenFinishRouteActionClient:
    def __init__(self) -> None:
        self.calls = 0
        self.product_id: str | None = None
        self.artifact_id: str | None = None

    def generate_action(self, context: dict):
        self.calls += 1
        received = [
            event
            for event in context.get("recentEvents", [])
            if event.get("type") == "USER_INPUT_RECEIVED"
        ]
        if not received:
            return parse_tool_action(
                """
                {
                  "tool": "ask_user",
                  "arguments": {
                    "reason": "需要确认风格。",
                    "question": "是否改为受其特质启发而非直接模仿？",
                    "suggestedOptions": ["按这个方向开始", "换一个方向"]
                  }
                }
                """
            )
        products = context.get("productManifest") or []
        if products:
            self.product_id = products[0]["id"]
            self.artifact_id = products[0]["latestArtifactId"]
        if self.product_id and self.artifact_id:
            return parse_tool_action(
                f"""
                {{
                  "tool": "finish_mission",
                  "arguments": {{
                    "reason": "用户已确认，产品已完成。",
                    "summary": "Answered mission complete.",
                    "finalProductIds": ["{self.product_id}"],
                    "finalArtifactIds": ["{self.artifact_id}"]
                  }}
                }}
                """
            )
        return parse_tool_action(
            """
            {
              "tool": "work_product",
              "arguments": {
                "reason": "按用户确认写入产品。",
                "operation": "create_product",
                "productId": null,
                "sourceArtifactIds": [],
                "productTitle": "Confirmed product",
                "artifactTitle": "Confirmed draft",
                "artifactKind": "draft",
                "content": "User confirmed direction. Draft follows the confirmed direction.",
                "summary": "Confirmed draft."
              }
            }
            """
        )


class WorkModeRoutesTest(TestCase):
    def setUp(self) -> None:
        self.service = WorkModeService(FakeWorkModeRepository())
        app = FastAPI()
        app.include_router(router, prefix="/api/work")
        app.dependency_overrides[get_current_user_id] = lambda: TEST_USER_ID
        app.dependency_overrides[get_work_mode_service] = lambda: self.service
        app.dependency_overrides[get_evaluator_runtime] = lambda: EvaluatorRuntime(self.service)
        app.dependency_overrides[get_user_service] = lambda: FakeUserService()
        app.dependency_overrides[get_work_mode_worker_launcher] = lambda: self.run_worker
        self.client = TestClient(app)

    def run_worker(self, user_id: str, mission_id: str, run_id: str) -> None:
        MissionLoopRunner(self.service, ScriptedRouteActionClient(), max_turns=5).run(user_id, mission_id, run_id)

    def test_project_mission_start_and_events_routes(self) -> None:
        project_response = self.client.post(
            "/api/work/projects",
            json={"name": "Cyber1924"},
        )
        self.assertEqual(project_response.status_code, 201)
        project = project_response.json()
        self.assertEqual(project["repoPath"], "")

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Fix OAuth",
                "goal": "Fix Google OAuth login.",
            },
        )
        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()

        start_response = self.client.post(f"/api/work/missions/{mission['id']}/start", json={})
        self.assertEqual(start_response.status_code, 200)
        started = start_response.json()
        self.assertEqual(started["mission"]["status"], "running")
        self.assertEqual(started["activeRun"]["status"], "running")

        events_response = self.client.get(f"/api/work/missions/{mission['id']}/events")
        self.assertEqual(events_response.status_code, 200)
        event_types = [event["type"] for event in events_response.json()]
        self.assertIn("MISSION_STARTED", event_types)
        self.assertIn("MISSION_PLAN_UPDATED", event_types)
        self.assertIn("PRODUCT_UPDATED", event_types)
        self.assertEqual(event_types[-1], "MISSION_COMPLETED")

        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["mission"]["status"], "completed")
        self.assertEqual(len(detail["artifacts"]), 1)
        self.assertEqual(len(detail["products"]), 1)
        self.assertIn("Route generated artifact.", detail["artifacts"][0]["content"])

    def test_start_route_launches_worker_without_fastapi_background_task(self) -> None:
        calls: list[tuple[str, str, str]] = []
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: (
            lambda user_id, mission_id, run_id: calls.append((user_id, mission_id, run_id))
        )
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run."},
        ).json()

        response = self.client.post(f"/api/work/missions/{mission['id']}/start", json={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mission"]["status"], "running")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], mission["id"])

    def test_mission_detail_response_includes_artifacts(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Draft", "goal": "Write one scene."},
        ).json()
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()

        self.assertEqual(detail["artifacts"], [])
        self.assertEqual(detail["products"], [])
        self.assertEqual(detail["workWindows"], [])

    def test_events_route_serializes_invalid_model_turn_events(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Draft", "goal": "Write one scene."},
        ).json()
        mission_document = self.service._require_mission(TEST_USER_ID, mission["id"])
        self.service.append_event(
            TEST_USER_ID,
            mission_document,
            run=None,
            step=None,
            event_type="MODEL_TURN_INVALID",
            title="Invalid turn",
            message="tool_action_schema_invalid",
            payload={"code": "tool_action_schema_invalid"},
        )

        response = self.client.get(f"/api/work/missions/{mission['id']}/events")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[-1]["type"], "MODEL_TURN_INVALID")

    def test_event_stream_route_streams_persisted_events_in_order(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Stream"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Stream Mission", "goal": "Run."},
        ).json()
        self.client.post(f"/api/work/missions/{mission['id']}/start", json={})

        response = self.client.get(f"/api/work/missions/{mission['id']}/events/stream?afterSequence=0")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        body = response.text
        self.assertIn("event: work_event", body)
        self.assertIn("data:", body)
        self.assertIn('"type": "MISSION_CREATED"', body)
        self.assertIn('"type": "MISSION_COMPLETED"', body)

    def test_event_stream_helper_respects_after_sequence_cursor(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Stream Cursor"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Cursor Mission", "goal": "Run."},
        ).json()
        self.client.post(f"/api/work/missions/{mission['id']}/start", json={})
        events = self.service.list_events(TEST_USER_ID, mission["id"])

        chunks = list(
            _mission_event_stream(
                self.service,
                TEST_USER_ID,
                mission["id"],
                after_sequence=events[-2]["sequence"],
                poll_seconds=0,
                ping_seconds=999,
            )
        )

        body = "".join(chunks)
        self.assertIn('"type": "MISSION_COMPLETED"', body)
        self.assertNotIn('"type": "MISSION_CREATED"', body)

    def test_event_stream_helper_pings_when_running_and_idle(self) -> None:
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: lambda user_id, mission_id, run_id: None
        project = self.client.post("/api/work/projects", json={"name": "Stream Ping"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Ping Mission", "goal": "Run."},
        ).json()
        self.client.post(f"/api/work/missions/{mission['id']}/start", json={})
        events = self.service.list_events(TEST_USER_ID, mission["id"])

        chunks = list(
            _mission_event_stream(
                self.service,
                TEST_USER_ID,
                mission["id"],
                after_sequence=events[-1]["sequence"],
                poll_seconds=0,
                ping_seconds=0,
                max_idle_polls=1,
            )
        )

        self.assertEqual("".join(chunks), 'event: ping\ndata: {"status": "ok"}\n\n')

    def test_evaluate_route_persists_reliability_report(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Research"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Toronto AI research",
                "goal": "Find 3 Toronto AI companies with source link.",
            },
        ).json()
        started = self.client.post(f"/api/work/missions/{mission['id']}/start", json={}).json()
        run_id = started["latestRun"]["id"]
        product = self.service.create_product(
            TEST_USER_ID,
            mission["id"],
            title="Research",
            summary="Research result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
        )
        artifact = self.service.create_product_artifact(
            TEST_USER_ID,
            mission["id"],
            run_id,
            product["id"],
            kind="final",
            title="Research final",
            content="Cohere is a Toronto enterprise AI company. Source: https://cohere.com",
            summary="Research result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
            source_artifact_ids=[],
            work_window_id=None,
            metadata={"summary": "Research result."},
        )
        self.service.mark_product_final(TEST_USER_ID, product["id"])
        self.service.mark_mission_completed(
            TEST_USER_ID,
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[artifact["id"]],
            summary="Done.",
        )

        response = self.client.post(f"/api/work/missions/{mission['id']}/evaluate", json={})

        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail["events"][-1]["type"], "RELIABILITY_REPORTED")
        self.assertTrue(
            any(item["metadata"].get("artifactRole") == "reliability_report" for item in detail["artifacts"])
        )

    def test_answer_route_records_input_and_resumes_waiting_mission(self) -> None:
        action_client = AskThenFinishRouteActionClient()
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: (
            lambda user_id, mission_id, run_id: MissionLoopRunner(self.service, action_client, max_turns=6).run(
                user_id,
                mission_id,
                run_id,
            )
        )
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Style", "goal": "Ask before writing."},
        ).json()
        first_start = self.client.post(f"/api/work/missions/{mission['id']}/start", json={})
        waiting = self.client.get(f"/api/work/missions/{mission['id']}").json()

        self.assertEqual(first_start.status_code, 200)
        self.assertEqual(waiting["mission"]["status"], "waiting_input")
        self.assertEqual(waiting["events"][-1]["type"], "USER_INPUT_REQUESTED")

        answer_response = self.client.post(
            f"/api/work/missions/{mission['id']}/answer",
            json={"answer": "按这个方向开始。"},
        )

        self.assertEqual(answer_response.status_code, 200)
        answered = answer_response.json()
        self.assertEqual(answered["mission"]["status"], "running")

        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        event_types = [event["type"] for event in detail["events"]]
        self.assertIn("USER_INPUT_RECEIVED", event_types)
        self.assertEqual(detail["mission"]["status"], "completed")
        self.assertEqual(detail["activeRun"], None)
        self.assertEqual(len(detail["products"]), 1)
        self.assertGreaterEqual(action_client.calls, 3)

    def test_follow_up_route_records_request_and_launches_new_run(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Follow Up"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Draft", "goal": "Write a draft."},
        ).json()
        completed = self.client.post(f"/api/work/missions/{mission['id']}/start", json={}).json()
        self.assertEqual(completed["mission"]["status"], "running")
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["mission"]["status"], "completed")
        calls: list[tuple[str, str, str]] = []
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: (
            lambda user_id, mission_id, run_id: calls.append((user_id, mission_id, run_id))
        )

        response = self.client.post(
            f"/api/work/missions/{mission['id']}/follow-up",
            json={"request": "Add an English version."},
        )

        self.assertEqual(response.status_code, 200)
        continued = response.json()
        self.assertEqual(continued["mission"]["status"], "running")
        self.assertEqual(continued["activeRun"]["metadata"]["resumeReason"], "user_followup")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], mission["id"])
        event_types = [event["type"] for event in continued["events"]]
        self.assertIn("USER_FOLLOWUP_REQUESTED", event_types)
        follow_up_event = next(event for event in continued["events"] if event["type"] == "USER_FOLLOWUP_REQUESTED")
        self.assertEqual(follow_up_event["payload"]["request"], "Add an English version.")

    def test_stop_route_requires_running_mission(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run V0."},
        ).json()

        response = self.client.post(f"/api/work/missions/{mission['id']}/stop", json={"reason": "pause"})

        self.assertEqual(response.status_code, 409)

    def test_stop_route_records_stop_requested_for_running_mission(self) -> None:
        self.client.app.dependency_overrides[get_work_mode_worker_launcher] = lambda: lambda user_id, mission_id, run_id: None
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        mission = self.client.post(
            "/api/work/missions",
            json={"projectId": project["id"], "title": "Mission", "goal": "Run V0."},
        ).json()
        self.client.post(f"/api/work/missions/{mission['id']}/start", json={})

        response = self.client.post(f"/api/work/missions/{mission['id']}/stop", json={"reason": "pause"})

        self.assertEqual(response.status_code, 200)
        detail = response.json()
        self.assertEqual(detail["mission"]["status"], "stopping")
        self.assertEqual(detail["activeRun"]["status"], "running")
        self.assertEqual(
            [event["type"] for event in detail["events"]],
            ["MISSION_CREATED", "MISSION_STARTED", "MISSION_STOP_REQUESTED"],
        )

    def test_employee_routes_allow_project_lead_selection(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Demo"}).json()
        employee_response = self.client.post(
            "/api/work/employees",
            json={
                "name": "Mira",
                "role": "Designer",
                "personality": "Calm",
                "experience": ["Dashboards"],
                "skills": ["ux"],
                "permissions": {"can_edit_files": False},
            },
        )
        self.assertEqual(employee_response.status_code, 201)
        employee = employee_response.json()

        add_response = self.client.post(
            f"/api/work/projects/{project['id']}/employees",
            json={"employeeId": employee["id"], "roleOnProject": "Lead"},
        )
        self.assertEqual(add_response.status_code, 201)

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Mission",
                "goal": "Run V0.",
                "leadEmployeeId": employee["id"],
            },
        )

        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()
        self.assertEqual(mission["leadEmployeeName"], "Mira")
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["events"][0]["payload"]["employee"]["name"], "Mira")

    def test_mission_route_accepts_user_agent_lead_without_team_setup(self) -> None:
        project = self.client.post("/api/work/projects", json={"name": "Novel"}).json()

        mission_response = self.client.post(
            "/api/work/missions",
            json={
                "projectId": project["id"],
                "title": "Outline",
                "goal": "Plan the novel.",
                "leadEmployeeId": "agent_1",
            },
        )

        self.assertEqual(mission_response.status_code, 201)
        mission = mission_response.json()
        self.assertEqual(mission["leadEmployeeId"], "agent_1")
        self.assertEqual(mission["leadEmployeeName"], "Planner")
        self.assertEqual(mission["leadEmployeeRole"], "careful planner")
        detail = self.client.get(f"/api/work/missions/{mission['id']}").json()
        self.assertEqual(detail["events"][0]["payload"]["employee"]["id"], "agent_1")
        self.assertEqual(detail["events"][0]["payload"]["employee"]["name"], "Planner")
