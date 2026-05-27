"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import HTTPException

from work_mode.schemas import MissionCreateRequest, MissionStartRequest, ProjectCreateRequest
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from work_mode.tool_protocol import parse_tool_action


class WorkModeToolExecutorTest(TestCase):
    def setUp(self) -> None:
        self.repository = FakeWorkModeRepository()
        self.service = WorkModeService(self.repository)
        self.executor = WorkModeToolExecutor(self.service)

    def test_delegate_agent_creates_visible_window_and_result_artifact(self) -> None:
        mission, run_id = self._started_agent_mission()
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="雨夜车站",
            summary="长篇小说。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )
        delegate_client = ScriptedDelegateClient(
            """
            {
              "status": "completed",
              "title": "第一章草稿",
              "summary": "完成第一章草稿。",
              "content": "雨夜里，旧车站只剩一盏灯。",
              "reason": "按 brief 输出章节草稿。"
            }
            """
        )
        executor = WorkModeToolExecutor(self.service, delegate_client=delegate_client)

        result = executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "delegate_agent",
                  "arguments": {{
                    "reason": "让写作 Agent 起草第一章。",
                    "agentSlot": "agent_2",
                    "windowTitle": "第一章草稿",
                    "brief": "写出第一章正文。",
                    "expectedOutput": "chapter",
                    "targetProductId": "{product["id"]}",
                    "sourceArtifactIds": []
                  }}
                }}
                """
            ),
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in completed["events"]]

        self.assertFalse(result.terminal)
        self.assertIn("WORK_WINDOW_OPENED", event_types)
        self.assertIn("WORK_WINDOW_COMPLETED", event_types)
        self.assertIn("PRODUCT_UPDATED", event_types)
        self.assertEqual(len(completed["workWindows"]), 1)
        self.assertEqual(completed["workWindows"][0]["status"], "completed")
        self.assertEqual(completed["workWindows"][0]["agentSlot"], "agent_2")
        self.assertEqual(completed["workWindows"][0]["resultArtifactId"], completed["artifacts"][0]["id"])
        self.assertEqual(completed["artifacts"][0]["metadata"]["workWindowId"], completed["workWindows"][0]["id"])
        self.assertIn("旧车站", completed["artifacts"][0]["content"])
        self.assertEqual(delegate_client.calls, 1)
        self.assertNotIn("availableTools", delegate_client.last_context)

    def test_inspect_product_is_bounded_and_visible(self) -> None:
        mission, run_id = self._started_agent_mission()
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="雨夜车站",
            summary="长篇小说。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind="chapter",
            title="第一章",
            content="车站" * 2000,
            summary="第一章草稿。",
            created_by={"id": "agent_2", "name": "Writer", "role": "delegate"},
            source_artifact_ids=[],
            work_window_id=None,
        )

        result = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "inspect_product",
                  "arguments": {{
                    "reason": "检查章节长度。",
                    "productIds": ["{product["id"]}"],
                    "artifactIds": ["{artifact["id"]}"],
                    "focus": "看第一章是否可继续扩写。"
                  }}
                }}
                """
            ),
        )

        completed = self.service.get_mission_detail("user_1", mission["id"])
        inspect_event = [event for event in completed["events"] if event["type"] == "PRODUCT_INSPECTED"][-1]

        self.assertFalse(result.terminal)
        self.assertEqual(len(result.observation["inspected"]), 1)
        self.assertLessEqual(len(result.observation["inspected"][0]["excerpt"]), 2400)
        self.assertEqual(inspect_event["payload"]["artifactIds"], [artifact["id"]])
        self.assertIn("看第一章", inspect_event["message"])

    def test_ask_user_and_block_mission_create_terminal_states(self) -> None:
        mission, run_id = self._started_agent_mission()

        ask_result = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                """
                {
                  "tool": "ask_user",
                  "arguments": {
                    "reason": "需要确认题材。",
                    "question": "要现实主义还是悬疑？",
                    "suggestedOptions": ["现实主义", "悬疑"]
                  }
                }
                """
            ),
        )
        waiting = self.service.get_mission_detail("user_1", mission["id"])

        self.assertTrue(ask_result.terminal)
        self.assertEqual(waiting["mission"]["status"], "waiting_input")
        self.assertEqual(waiting["events"][-1]["type"], "USER_INPUT_REQUESTED")

        blocked_mission, blocked_run_id = self._started_agent_mission()
        block_result = self.executor.execute(
            "user_1",
            blocked_mission["id"],
            blocked_run_id,
            parse_tool_action(
                """
                {
                  "tool": "block_mission",
                  "arguments": {
                    "reason": "缺少必要设定。",
                    "blockedReason": "无法判断用户禁止的题材边界。",
                    "neededFromUser": "请给出题材禁区。"
                  }
                }
                """
            ),
        )
        blocked = self.service.get_mission_detail("user_1", blocked_mission["id"])

        self.assertTrue(block_result.terminal)
        self.assertEqual(blocked["mission"]["status"], "blocked")
        self.assertEqual(blocked["latestRun"]["status"], "blocked")
        self.assertEqual(blocked["events"][-1]["type"], "MISSION_BLOCKED")

    def test_finish_mission_rejects_missing_final_product(self) -> None:
        mission, run_id = self._started_agent_mission()

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    """
                    {
                      "tool": "finish_mission",
                      "arguments": {
                        "reason": "错误完成。",
                        "summary": "没有真实产品。",
                        "finalProductIds": ["missing_product"],
                        "finalArtifactIds": []
                      }
                    }
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 404)
        detail = self.service.get_mission_detail("user_1", mission["id"])
        self.assertEqual(detail["mission"]["status"], "running")

    def _started_agent_mission(self) -> tuple[dict, str]:
        project = self.service.create_project("user_1", ProjectCreateRequest(name="Novel"))
        mission = self.service.create_mission(
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
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        return mission, detail["activeRun"]["id"]


class ScriptedDelegateClient:
    def __init__(self, raw_result: str):
        self.raw_result = raw_result
        self.calls = 0
        self.last_context: dict | None = None

    def generate_delegate_result(self, context: dict):
        self.calls += 1
        self.last_context = context
        return self.raw_result
