"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
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

    def test_delegate_agent_persists_unstructured_text_as_window_artifact(self) -> None:
        mission, run_id = self._started_agent_mission()
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="雨夜车站",
            summary="长篇小说。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )
        delegate_client = ScriptedDelegateClient("第一章\n\n雨夜里，旧车站只剩一盏灯。")
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

        detail = self.service.get_mission_detail("user_1", mission["id"])
        artifact = detail["artifacts"][0]

        self.assertFalse(result.terminal)
        self.assertEqual(detail["workWindows"][0]["status"], "completed")
        self.assertIn("旧车站", artifact["content"])
        self.assertFalse(artifact["metadata"]["delegateStructured"])

    def test_delegate_agent_parses_fenced_json_result(self) -> None:
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
            ```json
            {"status":"completed","title":"第二章","summary":"完成第二章。","content":"第二章正文。","reason":"按 brief 完成。"}
            ```
            """
        )
        executor = WorkModeToolExecutor(self.service, delegate_client=delegate_client)

        executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "delegate_agent",
                  "arguments": {{
                    "reason": "让写作 Agent 起草第二章。",
                    "agentSlot": "agent_2",
                    "windowTitle": "第二章草稿",
                    "brief": "写出第二章正文。",
                    "expectedOutput": "chapter",
                    "targetProductId": "{product["id"]}",
                    "sourceArtifactIds": []
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])

        self.assertEqual(detail["workWindows"][0]["status"], "completed")
        self.assertEqual(detail["artifacts"][0]["title"], "第二章")
        self.assertTrue(detail["artifacts"][0]["metadata"]["delegateStructured"])

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

    def test_finish_mission_rejects_missing_final_artifact(self) -> None:
        mission, run_id = self._started_agent_mission()
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="雨夜车站",
            summary="长篇小说。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "错误完成。",
                        "summary": "Artifact 不存在。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["missing_artifact"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 404)
        detail = self.service.get_mission_detail("user_1", mission["id"])
        self.assertEqual(detail["mission"]["status"], "running")
        self.assertEqual(detail["products"][0]["status"], "active")

    def test_finish_mission_event_records_final_lineage(self) -> None:
        mission, run_id = self._started_agent_mission(title="写短篇小说", goal="写一个短篇小说。")
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
            kind="final",
            title="最终成稿",
            content="雨夜车站最终成稿。",
            summary="最终成稿完成。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
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
                  "tool": "finish_mission",
                  "arguments": {{
                    "reason": "最终成稿已完成。",
                    "summary": "完成。",
                    "finalProductIds": ["{product["id"]}"],
                    "finalArtifactIds": ["{artifact["id"]}"]
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        completed_event = detail["events"][-1]

        self.assertTrue(result.terminal)
        self.assertEqual(detail["mission"]["status"], "completed")
        self.assertEqual(detail["products"][0]["status"], "final")
        self.assertEqual(detail["products"][0]["deliverableArtifactId"], artifact["id"])
        self.assertEqual(detail["products"][0]["deliveryStatus"], "verified_final")
        self.assertEqual(completed_event["type"], "MISSION_COMPLETED")
        self.assertEqual(completed_event["payload"]["finalProductIds"], [product["id"]])
        self.assertEqual(completed_event["payload"]["finalArtifactIds"], [artifact["id"]])

    def test_finish_mission_rejects_8000_novel_outline_only_final(self) -> None:
        mission, run_id = self._started_agent_mission(goal="写一个8000字中文小说，题材自定，要求分章节。")
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
            kind="outline",
            title="故事大纲",
            content="这是一个大纲。",
            summary="只有大纲。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
            source_artifact_ids=[],
            work_window_id=None,
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "试图完成。",
                        "summary": "只有大纲。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["{artifact["id"]}"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "final_artifact_not_final_content")

    def test_finish_mission_rejects_8000_novel_short_final(self) -> None:
        mission, run_id = self._started_agent_mission(goal="写一个8000字中文小说，题材自定。")
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
            kind="final",
            title="最终成稿",
            content="短篇终稿。",
            summary="太短。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
            source_artifact_ids=[],
            work_window_id=None,
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "试图完成。",
                        "summary": "太短。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["{artifact["id"]}"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "final_artifact_cjk_too_short")

    def test_review_product_persists_review_artifact_without_mutating_source(self) -> None:
        mission, run_id = self._started_agent_mission(title="写短篇小说", goal="写一个短篇小说。")
        product, artifact = self._product_with_artifact(mission, run_id, content="第一章正文。", kind="chapter")

        result = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "review_product",
                  "arguments": {{
                    "reason": "终稿前审核。",
                    "productIds": ["{product["id"]}"],
                    "artifactIds": ["{artifact["id"]}"],
                    "reviewTitle": "小说审核",
                    "reviewProfile": "general_text_v1",
                    "verdict": "needs_revision",
                    "score": 72,
                    "summary": "需要补足人物动机。",
                    "findings": [
                      {{
                        "severity": "major",
                        "area": "structure",
                        "claim": "人物动机不足。",
                        "evidence": "正文没有解释主角为何行动。",
                        "requiredChange": "补一段行动动机。"
                      }}
                    ],
                    "passedChecks": [],
                    "recommendedNextTool": "work_product"
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        review_artifact = next(item for item in detail["artifacts"] if item["kind"] == "report")

        self.assertFalse(result.terminal)
        self.assertEqual(detail["events"][-1]["type"], "PRODUCT_REVIEWED")
        self.assertEqual(review_artifact["metadata"]["artifactRole"], "review")
        self.assertEqual(review_artifact["metadata"]["sourceArtifactIds"], [artifact["id"]])
        self.assertEqual(review_artifact["metadata"]["verdict"], "needs_revision")
        self.assertIn("人物动机不足", review_artifact["content"])
        self.assertEqual(detail["artifacts"][0]["content"], "第一章正文。")

    def test_discuss_with_delegate_creates_discussion_window_and_artifact(self) -> None:
        mission, run_id = self._started_agent_mission(title="写短篇小说", goal="写一个短篇小说。")
        product, artifact = self._product_with_artifact(mission, run_id, content="第二章正文。", kind="chapter")
        delegate_client = ScriptedDelegateClient(
            """
            {
              "status": "completed",
              "title": "第二章修订讨论",
              "summary": "建议增加父亲旧票线索。",
              "transcript": [
                {"speaker": "lead", "content": "怎样补足线索？"},
                {"speaker": "delegate", "content": "可以在检票口加入旧票。"}
              ],
              "recommendation": "在第二章中加入旧票和父亲姓名。",
              "reason": "讨论完成。"
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
                  "tool": "discuss_with_delegate",
                  "arguments": {{
                    "reason": "和章节作者讨论修订方向。",
                    "agentSlot": "agent_2",
                    "discussionTitle": "第二章修订讨论",
                    "windowId": null,
                    "productId": "{product["id"]}",
                    "artifactIds": ["{artifact["id"]}"],
                    "question": "第二章怎样补足父亲线索？",
                    "expectedOutcome": "给出可执行修订建议。",
                    "maxTurns": 1
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        event_types = [event["type"] for event in detail["events"]]
        discussion_window = next(window for window in detail["workWindows"] if window["metadata"].get("windowType") == "discussion")
        discussion_artifact = next(item for item in detail["artifacts"] if item["metadata"].get("artifactRole") == "discussion")

        self.assertFalse(result.terminal)
        self.assertIn("DISCUSSION_WINDOW_OPENED", event_types)
        self.assertIn("DISCUSSION_WINDOW_COMPLETED", event_types)
        self.assertEqual(discussion_window["status"], "completed")
        self.assertEqual(discussion_window["resultArtifactId"], discussion_artifact["id"])
        self.assertEqual(discussion_artifact["metadata"]["sourceArtifactIds"], [artifact["id"]])
        self.assertIn("旧票", discussion_artifact["content"])

    def test_discuss_with_delegate_coerces_partial_json_into_discussion_artifact(self) -> None:
        mission, run_id = self._started_agent_mission(title="写论文", goal="写一篇文献综述。")
        product, artifact = self._product_with_artifact(mission, run_id, content="终稿候选正文。", kind="draft")
        delegate_client = ScriptedDelegateClient(
            """
            {
              "summary": "建议先补齐参考文献，再压缩重复论述。",
              "recommendation": "不要直接收尾；先追加参考文献段落，再生成最终稿。",
              "reason": "讨论结果可执行。"
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
                  "tool": "discuss_with_delegate",
                  "arguments": {{
                    "reason": "讨论是否可以收尾。",
                    "agentSlot": "agent_2",
                    "discussionTitle": "终稿候选讨论",
                    "windowId": null,
                    "productId": "{product["id"]}",
                    "artifactIds": ["{artifact["id"]}"],
                    "question": "这版是否可以作为最终稿？",
                    "expectedOutcome": "给出继续或收尾建议。",
                    "maxTurns": 1
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        discussion_window = next(window for window in detail["workWindows"] if window["metadata"].get("windowType") == "discussion")
        discussion_artifact = next(item for item in detail["artifacts"] if item["metadata"].get("artifactRole") == "discussion")

        self.assertFalse(result.terminal)
        self.assertEqual(result.observation["status"], "ok")
        self.assertEqual(discussion_window["status"], "completed")
        self.assertIn("补齐参考文献", discussion_artifact["content"])
        self.assertIn("不要直接收尾", discussion_artifact["content"])

    def test_web_search_persists_bounded_search_event(self) -> None:
        mission, run_id = self._started_agent_mission(title="查资料", goal="查找一个可引用资料。")
        executor = WorkModeToolExecutor(
            self.service,
            search_provider=FakeSearchProvider(
                [
                    {
                        "title": "Source A",
                        "url": "https://example.com/a",
                        "source": "example.com",
                        "snippet": "第一条资料摘要。",
                        "publishedAt": "2026-05-01",
                    },
                    {
                        "title": "Source B",
                        "url": "https://example.com/b",
                        "source": "example.com",
                        "snippet": "第二条资料摘要。",
                        "publishedAt": None,
                    },
                ]
            ),
        )

        result = executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                """
                {
                  "tool": "web_search",
                  "arguments": {
                    "reason": "需要外部资料。",
                    "query": "latest source backed reference",
                    "searchType": "reference",
                    "maxResults": 2,
                    "recencyDays": 30,
                    "allowedDomains": ["example.com"],
                    "blockedDomains": []
                  }
                }
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        event = detail["events"][-1]

        self.assertFalse(result.terminal)
        self.assertEqual(result.observation["tool"], "web_search")
        self.assertEqual(result.observation["status"], "ok")
        self.assertEqual(len(result.observation["results"]), 2)
        self.assertEqual(result.observation["effectiveQuery"], "latest source backed reference")
        self.assertFalse(result.observation["fallbackApplied"])
        self.assertEqual(result.observation["attemptCount"], 1)
        self.assertEqual(event["type"], "WEB_SEARCH_COMPLETED")
        self.assertEqual(event["payload"]["query"], "latest source backed reference")
        self.assertEqual(event["payload"]["effectiveQuery"], "latest source backed reference")
        self.assertEqual(event["payload"]["results"][0]["url"], "https://example.com/a")

    def test_web_search_failure_is_visible_and_non_terminal(self) -> None:
        mission, run_id = self._started_agent_mission(title="查资料", goal="查找一个可引用资料。")
        executor = WorkModeToolExecutor(
            self.service,
            search_provider=FailingSearchProvider("search_timeout", retryable=True),
        )

        result = executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                """
                {
                  "tool": "web_search",
                  "arguments": {
                    "reason": "需要外部资料。",
                    "query": "latest source backed reference",
                    "searchType": "reference",
                    "maxResults": 2,
                    "recencyDays": 30,
                    "allowedDomains": [],
                    "blockedDomains": []
                  }
                }
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        event = detail["events"][-1]

        self.assertFalse(result.terminal)
        self.assertEqual(result.observation["status"], "failed")
        self.assertEqual(result.observation["code"], "search_timeout")
        self.assertTrue(result.observation["retryable"])
        self.assertEqual(result.observation["effectiveQuery"], "latest source backed reference")
        self.assertEqual(event["type"], "WEB_SEARCH_FAILED")
        self.assertEqual(detail["mission"]["status"], "running")

    def test_evaluate_product_persists_reliability_report_observation(self) -> None:
        mission, run_id = self._started_agent_mission(title="研究论文", goal="写一篇关于海地革命的研究论文，需要有最终稿。")
        product, artifact = self._product_with_artifact(
            mission,
            run_id,
            content=paper_final_text(),
            kind="final",
        )

        result = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "evaluate_product",
                  "arguments": {{
                    "reason": "终稿前检查论文可靠性。",
                    "profile": "research_reliability_v1",
                    "productIds": ["{product["id"]}"],
                    "artifactIds": ["{artifact["id"]}"],
                    "focus": "检查最终稿和来源证据。"
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        report_artifact = next(item for item in detail["artifacts"] if item["metadata"].get("artifactRole") == "reliability_report")
        report_event = detail["events"][-1]
        event_types = [event["type"] for event in detail["events"]]

        self.assertFalse(result.terminal)
        self.assertEqual(result.observation["tool"], "evaluate_product")
        self.assertEqual(result.observation["status"], "ok")
        self.assertEqual(result.observation["reportArtifactId"], report_artifact["id"])
        self.assertEqual(result.observation["reliabilityStatus"], "needs_human_review")
        self.assertEqual(result.observation["recommendedNextTool"], "web_search")
        self.assertIn("EVALUATION_STARTED", event_types)
        self.assertEqual(report_event["type"], "RELIABILITY_REPORTED")

    def test_evaluate_product_can_recommend_revision_after_supported_search(self) -> None:
        mission, run_id = self._started_agent_mission(
            title="研究报告",
            goal="Assess the Toronto AI startup claims.",
        )
        mission_document = self.service._require_mission("user_1", mission["id"])
        self.service.append_event(
            "user_1",
            mission_document,
            run={"_id": run_id},
            step=None,
            event_type="WEB_SEARCH_COMPLETED",
            title="Search",
            message="Toronto AI startups",
            payload={
                "tool": "web_search",
                "status": "ok",
                "query": "Toronto AI startups",
                "provider": "fake",
                "results": [
                    {
                        "title": "Cohere enterprise AI",
                        "url": "https://cohere.com",
                        "source": "cohere.com",
                        "snippet": "Cohere provides enterprise AI models and is headquartered in Toronto.",
                    }
                ],
            },
        )
        product, artifact = self._product_with_artifact(
            mission,
            run_id,
            content=(
                "Cohere is a Toronto enterprise AI company. Source: https://cohere.com\n"
                "MapleNeural Labs sells enterprise AI to banks. Source: https://mapleneural.example"
            ),
            kind="final",
        )

        result = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "evaluate_product",
                  "arguments": {{
                    "reason": "检查研究报告可靠性。",
                    "profile": "research_reliability_v1",
                    "productIds": ["{product["id"]}"],
                    "artifactIds": ["{artifact["id"]}"],
                    "focus": "检查来源和缺失项。"
                  }}
                }}
                """
            ),
        )

        self.assertEqual(result.observation["recommendedNextTool"], "work_product")
        self.assertTrue(result.observation["topIssues"])
        self.assertIn("type:unsupported_claim", result.observation["issueCounts"])

    def test_finish_mission_rejects_research_paper_outline_only_final(self) -> None:
        mission, run_id = self._started_agent_mission(title="研究论文", goal="写一篇关于海地革命的研究论文，需要最终稿。")
        product, artifact = self._product_with_artifact(
            mission,
            run_id,
            content="一、引言。二、正文。三、结论。本文将讨论海地革命的影响。",
            kind="outline",
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "尝试完成论文。",
                        "summary": "只有大纲。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["{artifact["id"]}"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "final_paper_draft_required")

    def test_finish_mission_requires_current_evaluation_for_research_paper(self) -> None:
        mission, run_id = self._started_agent_mission(title="研究论文", goal="写一篇关于海地革命的研究论文，需要最终稿。")
        product, artifact = self._product_with_artifact(
            mission,
            run_id,
            content=paper_final_text(),
            kind="final",
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "尝试完成论文。",
                        "summary": "论文完成。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["{artifact["id"]}"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "reliability_evaluation_required")

    def test_finish_mission_blocks_needs_review_research_paper_report(self) -> None:
        mission, run_id = self._started_agent_mission(title="研究论文", goal="写一篇关于海地革命的研究论文，需要最终稿。")
        product, artifact = self._product_with_artifact(
            mission,
            run_id,
            content=paper_final_text(),
            kind="final",
        )
        self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "evaluate_product",
                  "arguments": {{
                    "reason": "终稿前检查论文可靠性。",
                    "profile": "research_reliability_v1",
                    "productIds": ["{product["id"]}"],
                    "artifactIds": ["{artifact["id"]}"],
                    "focus": "检查最终稿和来源证据。"
                  }}
                }}
                """
            ),
        )

        with self.assertRaises(HTTPException) as error:
            self.executor.execute(
                "user_1",
                mission["id"],
                run_id,
                parse_tool_action(
                    f"""
                    {{
                      "tool": "finish_mission",
                      "arguments": {{
                        "reason": "尝试完成论文。",
                        "summary": "论文完成。",
                        "finalProductIds": ["{product["id"]}"],
                        "finalArtifactIds": ["{artifact["id"]}"]
                      }}
                    }}
                    """
                ),
            )

        self.assertEqual(error.exception.status_code, 422)
        self.assertEqual(error.exception.detail, "reliability_evaluation_needs_review")

    def test_revise_artifact_links_review_and_discussion_lineage(self) -> None:
        mission, run_id = self._started_agent_mission(title="写短篇小说", goal="写一个短篇小说。")
        product, artifact = self._product_with_artifact(mission, run_id, content="原始正文。", kind="draft")

        revised = self.executor.execute(
            "user_1",
            mission["id"],
            run_id,
            parse_tool_action(
                f"""
                {{
                  "tool": "work_product",
                  "arguments": {{
                    "reason": "根据审核修订。",
                    "operation": "revise_artifact",
                    "productId": "{product["id"]}",
                    "sourceArtifactIds": ["{artifact["id"]}"],
                    "productTitle": "雨夜车站",
                    "artifactTitle": "第一章修订稿",
                    "artifactKind": "revision",
                    "content": "修订后正文。",
                    "summary": "补足人物动机。"
                  }}
                }}
                """
            ),
        )

        detail = self.service.get_mission_detail("user_1", mission["id"])
        source_artifact = next(item for item in detail["artifacts"] if item["id"] == artifact["id"])
        revision_artifact = next(item for item in detail["artifacts"] if item["id"] == revised.artifact_id)

        self.assertEqual(source_artifact["content"], "原始正文。")
        self.assertEqual(revision_artifact["metadata"]["sourceArtifactIds"], [artifact["id"]])
        self.assertEqual(revision_artifact["metadata"]["operation"], "revise_artifact")
        self.assertEqual(revision_artifact["metadata"]["revisionOf"], artifact["id"])
        self.assertEqual(revision_artifact["metadata"]["changeSummary"], "补足人物动机。")

    def _started_agent_mission(
        self,
        title: str = "写一个8000字小说",
        goal: str = "写一个8000字中文小说，题材自定。",
    ) -> tuple[dict, str]:
        project = self.service.create_project("user_1", ProjectCreateRequest(name="Novel"))
        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title=title,
                goal=goal,
                leadEmployeeId="agent_1",
            ),
            [
                {"slot": "agent_1", "name": "Planner", "voice": "lead", "personality": "Plans.", "story": ""},
                {"slot": "agent_2", "name": "Writer", "voice": "delegate", "personality": "Writes.", "story": ""},
            ],
        )
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        return mission, detail["activeRun"]["id"]

    def _product_with_artifact(
        self,
        mission: dict,
        run_id: str,
        content: str,
        kind: str,
    ) -> tuple[dict, dict]:
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="雨夜车站",
            summary="小说产品。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind=kind,
            title="章节草稿",
            content=content,
            summary="章节草稿。",
            created_by={"id": "agent_1", "name": "Planner", "role": "lead"},
            source_artifact_ids=[],
            work_window_id=None,
        )
        return product, artifact


class ScriptedDelegateClient:
    def __init__(self, raw_result: str):
        self.raw_result = raw_result
        self.calls = 0
        self.last_context: dict | None = None

    def generate_delegate_result(self, context: dict):
        self.calls += 1
        self.last_context = context
        return self.raw_result


class FakeSearchProvider:
    def __init__(self, results: list[dict]):
        self.results = results
        self.calls = 0
        self.last_request: dict | None = None

    def search(self, request: dict) -> dict:
        self.calls += 1
        self.last_request = request
        return {
            "status": "ok",
            "results": self.results,
            "truncated": False,
            "provider": "fake_search",
            "query": request["query"],
            "effectiveQuery": request["query"],
            "fallbackApplied": False,
            "fallbackReason": None,
            "attemptCount": 1,
        }


class FailingSearchProvider:
    def __init__(self, code: str, retryable: bool):
        self.code = code
        self.retryable = retryable

    def search(self, request: dict) -> dict:
        return {
            "status": "failed",
            "code": self.code,
            "retryable": self.retryable,
            "provider": "fake_search",
            "results": [],
            "truncated": False,
        }


def paper_final_text() -> str:
    return (
        "题目：海地革命的社会根源与大西洋世界影响\n\n"
        "引言：海地革命不是孤立的奴隶起义，而是法国殖民制度、种植园经济与启蒙政治语言共同作用的结果。"
        "本文认为，圣多明各被压迫群体把自由和平等的理念转化为组织行动，并最终改变了大西洋世界的权力结构。\n\n"
        "第一部分：殖民社会的结构性矛盾。圣多明各的财富建立在高度暴力化的奴隶劳动之上，"
        "白人种植园主、自由有色人和被奴役者之间的法律地位差异不断累积冲突。\n\n"
        "第二部分：革命政治语言的扩散。法国革命提供了新的合法性语言，但殖民地各阶层对自由和平等的解释并不相同，"
        "这种分歧推动了地方武装和政治联盟的重组。\n\n"
        "结论：海地革命的意义在于，它证明被压迫者并非只是欧洲政治的接受者，也能够主动重写现代自由的边界。"
    )
