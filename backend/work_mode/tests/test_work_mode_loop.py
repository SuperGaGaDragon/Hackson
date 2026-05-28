"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from work_mode.action_client import ToolActionClientError
from work_mode.loop import MissionLoopRunner
from work_mode.schemas import MissionCreateRequest, MissionStartRequest, ProjectCreateRequest
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from work_mode.tool_protocol import parse_tool_action


class WorkModeLoopTest(TestCase):
    def setUp(self) -> None:
        self.repository = FakeWorkModeRepository()
        self.service = WorkModeService(self.repository)

    def test_loop_executes_model_selected_plan_product_and_finish(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = ScriptedActionClient(
            [
                """
                {
                  "tool": "mission_plan",
                  "arguments": {
                    "reason": "先规划长篇结构。",
                    "planTitle": "小说计划",
                    "steps": [
                      {"title": "写大纲", "status": "completed", "notes": "完成。"},
                      {"title": "写正文", "status": "pending", "notes": "下一步。"}
                    ]
                  }
                }
                """,
                """
                {
                  "tool": "work_product",
                  "arguments": {
                    "reason": "创建第一版正文产品。",
                    "operation": "create_product",
                    "productId": null,
                    "sourceArtifactIds": [],
                    "productTitle": "雨夜车站",
                    "artifactTitle": "第一章",
                    "artifactKind": "chapter",
                    "content": "雨夜车站的故事开始了。",
                    "summary": "完成第一章。"
                  }
                }
                """,
                """
                {
                  "tool": "finish_mission",
                  "arguments": {
                    "reason": "已有最终产品。",
                    "summary": "小说初稿完成。",
                    "finalProductIds": ["$LAST_PRODUCT_ID"],
                    "finalArtifactIds": ["$LAST_ARTIFACT_ID"]
                  }
                }
                """,
            ]
        )

        MissionLoopRunner(self.service, action_client=action_client, max_turns=5).run("user_1", mission["id"], run_id)

        completed = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in completed["events"]]

        self.assertEqual(completed["mission"]["status"], "completed")
        self.assertIn("MISSION_PLAN_UPDATED", event_types)
        self.assertIn("MODEL_TURN_STARTED", event_types)
        self.assertIn("MODEL_TURN_COMPLETED", event_types)
        self.assertIn("TOOL_CALLED", event_types)
        self.assertIn("PRODUCT_UPDATED", event_types)
        self.assertEqual(event_types[-1], "MISSION_COMPLETED")
        self.assertEqual(len(completed["products"]), 1)
        self.assertEqual(completed["products"][0]["status"], "final")
        self.assertEqual(len(completed["artifacts"]), 1)
        self.assertEqual(action_client.calls, 3)

    def test_loop_retries_invalid_turn_then_continues(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = FailingThenScriptedActionClient(
            ToolActionClientError("tool_action_invalid_json", "model_turn_must_be_json"),
            """
            {
              "tool": "block_mission",
              "arguments": {
                "reason": "测试重试后正常调用工具。",
                "blockedReason": "测试终止。",
                "neededFromUser": ""
              }
            }
            """,
        )

        MissionLoopRunner(self.service, action_client=action_client, max_turns=3, max_invalid_turns=2).run(
            "user_1",
            mission["id"],
            run_id,
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(completed["mission"]["status"], "blocked")
        self.assertEqual(action_client.calls, 2)
        self.assertEqual(completed["events"][-1]["type"], "MISSION_BLOCKED")

    def test_loop_pauses_retryable_provider_error(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = AlwaysFailingActionClient(
            ToolActionClientError("model_timeout", "model_timeout", retryable=True)
        )

        MissionLoopRunner(self.service, action_client=action_client, max_turns=3, max_retryable_turn_retries=0).run(
            "user_1",
            mission["id"],
            run_id,
        )

        paused = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(paused["mission"]["status"], "paused_retryable")
        self.assertEqual(paused["latestRun"]["status"], "paused_retryable")
        self.assertEqual(paused["events"][-1]["type"], "MISSION_PAUSED_RETRYABLE")

    def test_loop_retries_retryable_provider_error_before_pausing(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = AlwaysFailingActionClient(
            ToolActionClientError("model_timeout", "model_timeout", retryable=True)
        )

        MissionLoopRunner(self.service, action_client=action_client, max_turns=3, max_retryable_turn_retries=1).run(
            "user_1",
            mission["id"],
            run_id,
        )

        paused = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in paused["events"]]

        self.assertEqual(paused["mission"]["status"], "paused_retryable")
        self.assertIn("MODEL_TURN_RETRYING", event_types)
        self.assertEqual(event_types[-1], "MISSION_PAUSED_RETRYABLE")

    def test_loop_pauses_and_marks_delegate_window_failed_on_delegate_timeout(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = ScriptedActionClient(
            [
                """
                {
                  "tool": "delegate_agent",
                  "arguments": {
                    "reason": "让写作 Agent 起草第一章。",
                    "agentSlot": "agent_2",
                    "windowTitle": "第一章草稿",
                    "brief": "写第一章。",
                    "expectedOutput": "chapter",
                    "targetProductId": null,
                    "sourceArtifactIds": []
                  }
                }
                """,
            ]
        )

        MissionLoopRunner(
            self.service,
            action_client=action_client,
            executor=WorkModeToolExecutor(
                self.service,
                delegate_client=FailingDelegateClient(
                    ToolActionClientError("model_timeout", "model_timeout", retryable=True)
                ),
            ),
            max_retryable_turn_retries=0,
        ).run("user_1", mission["id"], run_id)

        paused = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in paused["events"]]

        self.assertEqual(paused["mission"]["status"], "paused_retryable")
        self.assertEqual(paused["workWindows"][0]["status"], "failed")
        self.assertIn("WORK_WINDOW_FAILED", event_types)

    def test_loop_pauses_retryable_when_delegate_returns_invalid_structured_result(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        action_client = ScriptedActionClient(
            [
                """
                {
                  "tool": "delegate_agent",
                  "arguments": {
                    "reason": "让写作 Agent 起草第一章。",
                    "agentSlot": "agent_2",
                    "windowTitle": "第一章草稿",
                    "brief": "写第一章。",
                    "expectedOutput": "chapter",
                    "targetProductId": null,
                    "sourceArtifactIds": []
                  }
                }
                """,
            ]
        )

        MissionLoopRunner(
            self.service,
            action_client=action_client,
            executor=WorkModeToolExecutor(
                self.service,
                delegate_client=RawDelegateClient("{not valid json"),
            ),
            max_retryable_turn_retries=0,
        ).run("user_1", mission["id"], run_id)

        paused = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in paused["events"]]

        self.assertEqual(paused["mission"]["status"], "paused_retryable")
        self.assertEqual(paused["mission"]["lastError"], "delegate_result_invalid")
        self.assertEqual(paused["workWindows"][0]["status"], "failed")
        self.assertIn("WORK_WINDOW_FAILED", event_types)
        self.assertEqual(event_types[-1], "MISSION_PAUSED_RETRYABLE")

    def test_loop_resume_continues_from_persisted_product_manifest(self) -> None:
        mission = self._mission()
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        first_run_id = detail["activeRun"]["id"]
        first_client = FailingAfterProductActionClient()

        MissionLoopRunner(self.service, action_client=first_client, max_turns=4).run("user_1", mission["id"], first_run_id)
        paused = self.service.get_mission_detail("user_1", mission["id"])
        second_detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        second_run_id = second_detail["activeRun"]["id"]
        second_client = ResumeFromManifestActionClient()

        MissionLoopRunner(self.service, action_client=second_client, max_turns=4).run(
            "user_1",
            mission["id"],
            second_run_id,
        )
        completed = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(paused["mission"]["status"], "paused_retryable")
        self.assertNotEqual(first_run_id, second_run_id)
        self.assertEqual(completed["mission"]["status"], "completed")
        self.assertEqual(len(completed["products"]), 1)
        self.assertEqual(completed["products"][0]["status"], "final")
        self.assertTrue(second_client.saw_existing_product)

    def _mission(self) -> dict:
        project = self.service.create_project("user_1", ProjectCreateRequest(name="Novel"))
        return self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title="写一个8000字小说",
                goal="写一个8000字中文小说，题材自定。",
                leadEmployeeId="agent_1",
            ),
            [
                {"slot": "agent_1", "name": "Planner", "voice": "lead", "personality": "Plans.", "story": ""},
                {"slot": "agent_2", "name": "Writer", "voice": "delegate", "personality": "Writes.", "story": ""},
            ],
        )


class ScriptedActionClient:
    def __init__(self, actions: list[str]):
        self.actions = actions
        self.calls = 0
        self.last_product_id: str | None = None
        self.last_artifact_id: str | None = None

    def generate_action(self, context: dict):
        raw = self.actions[self.calls]
        raw = raw.replace("$LAST_PRODUCT_ID", self.last_product_id or "missing_product")
        raw = raw.replace("$LAST_ARTIFACT_ID", self.last_artifact_id or "missing_artifact")
        self.calls += 1
        return parse_tool_action(raw)


class FailingThenScriptedActionClient:
    def __init__(self, first_error: Exception, second_action: str):
        self.first_error = first_error
        self.second_action = second_action
        self.calls = 0

    def generate_action(self, context: dict):
        self.calls += 1
        if self.calls == 1:
            raise self.first_error
        return parse_tool_action(self.second_action)


class AlwaysFailingActionClient:
    def __init__(self, error: Exception):
        self.error = error
        self.calls = 0

    def generate_action(self, context: dict):
        self.calls += 1
        raise self.error


class FailingDelegateClient:
    def __init__(self, error: Exception):
        self.error = error

    def generate_delegate_result(self, context: dict):
        raise self.error


class RawDelegateClient:
    def __init__(self, result: str):
        self.result = result

    def generate_delegate_result(self, context: dict):
        return self.result


class FailingAfterProductActionClient:
    def __init__(self):
        self.calls = 0

    def generate_action(self, context: dict):
        self.calls += 1
        if self.calls == 1:
            return parse_tool_action(
                """
                {
                  "tool": "work_product",
                  "arguments": {
                    "reason": "先保存产品。",
                    "operation": "create_product",
                    "productId": null,
                    "sourceArtifactIds": [],
                    "productTitle": "雨夜车站",
                    "artifactTitle": "第一章",
                    "artifactKind": "chapter",
                    "content": "已有章节。",
                    "summary": "章节完成。"
                  }
                }
                """
            )
        raise ToolActionClientError("model_timeout", "model_timeout", retryable=True)


class ResumeFromManifestActionClient:
    def __init__(self):
        self.saw_existing_product = False

    def generate_action(self, context: dict):
        products = context.get("productManifest") or []
        self.saw_existing_product = bool(products)
        product = products[0]
        return parse_tool_action(
            f"""
            {{
              "tool": "finish_mission",
              "arguments": {{
                "reason": "继续已有产品并完成。",
                "summary": "恢复完成。",
                "finalProductIds": ["{product["id"]}"],
                "finalArtifactIds": ["{product["latestArtifactId"]}"]
              }}
            }}
            """
        )
