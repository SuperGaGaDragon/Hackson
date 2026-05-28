"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from work_mode.tool_protocol import ToolActionValidationError, parse_tool_action


class WorkModeToolProtocolTest(TestCase):
    def test_parses_valid_mission_plan_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "mission_plan",
              "arguments": {
                "reason": "先拆清楚小说结构。",
                "planTitle": "8000字小说计划",
                "steps": [
                  {"title": "确定主线", "status": "pending", "notes": "题材自定。"}
                ]
              }
            }
            """
        )

        self.assertEqual(action.tool, "mission_plan")
        self.assertEqual(action.arguments.reason, "先拆清楚小说结构。")
        self.assertEqual(action.arguments.steps[0].title, "确定主线")

    def test_parses_valid_work_product_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "work_product",
              "arguments": {
                "reason": "需要先创建小说产品。",
                "operation": "create_product",
                "productId": null,
                "sourceArtifactIds": [],
                "productTitle": "雨夜车站",
                "artifactTitle": "故事大纲",
                "artifactKind": "outline",
                "content": "一名年轻人追查旧车票背后的家族秘密。",
                "summary": "创建小说大纲。"
              }
            }
            """
        )

        self.assertEqual(action.tool, "work_product")
        self.assertEqual(action.arguments.operation, "create_product")
        self.assertIsNone(action.arguments.product_id)

    def test_rejects_plain_assistant_text(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action("好的，我先写一个大纲。")

        self.assertEqual(error.exception.code, "tool_action_invalid_json")

    def test_rejects_unknown_tool(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action('{"tool":"draw_react_component","arguments":{"reason":"show ui"}}')

        self.assertEqual(error.exception.code, "tool_action_unknown_tool")

    def test_rejects_multiple_tool_calls(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                [
                  {"tool": "mission_plan", "arguments": {"reason": "plan"}},
                  {"tool": "finish_mission", "arguments": {"reason": "done"}}
                ]
                """
            )

        self.assertEqual(error.exception.code, "tool_action_multiple_calls")

    def test_rejects_finish_without_final_product(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                {
                  "tool": "finish_mission",
                  "arguments": {
                    "reason": "已经完成。",
                    "summary": "完成。",
                    "finalProductIds": [],
                    "finalArtifactIds": []
                  }
                }
                """
            )

        self.assertEqual(error.exception.code, "tool_action_schema_invalid")

    def test_parses_valid_delegate_agent_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "delegate_agent",
              "arguments": {
                "reason": "长篇小说需要分章起草。",
                "agentSlot": "agent_2",
                "windowTitle": "第一章草稿",
                "brief": "按大纲写第一章，突出雨夜车站。",
                "expectedOutput": "chapter",
                "targetProductId": "product_1",
                "sourceArtifactIds": ["artifact_1"]
              }
            }
            """
        )

        self.assertEqual(action.tool, "delegate_agent")
        self.assertEqual(action.arguments.agent_slot, "agent_2")
        self.assertEqual(action.arguments.source_artifact_ids, ["artifact_1"])

    def test_parses_valid_inspect_ask_and_block_actions(self) -> None:
        inspect_action = parse_tool_action(
            """
            {
              "tool": "inspect_product",
              "arguments": {
                "reason": "整合前需要检查前文。",
                "productIds": ["product_1"],
                "artifactIds": ["artifact_1"],
                "focus": "人物动机"
              }
            }
            """
        )
        ask_action = parse_tool_action(
            """
            {
              "tool": "ask_user",
              "arguments": {
                "reason": "缺少题材约束。",
                "question": "你希望小说是什么题材？",
                "suggestedOptions": ["悬疑", "科幻"]
              }
            }
            """
        )
        block_action = parse_tool_action(
            """
            {
              "tool": "block_mission",
              "arguments": {
                "reason": "缺少必要授权。",
                "blockedReason": "无法继续。",
                "neededFromUser": "请补充目标。"
              }
            }
            """
        )

        self.assertEqual(inspect_action.arguments.product_ids, ["product_1"])
        self.assertEqual(ask_action.arguments.suggested_options, ["悬疑", "科幻"])
        self.assertEqual(block_action.arguments.blocked_reason, "无法继续。")

    def test_rejects_append_artifact_without_product_id(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                {
                  "tool": "work_product",
                  "arguments": {
                    "reason": "继续写。",
                    "operation": "append_artifact",
                    "productId": null,
                    "sourceArtifactIds": [],
                    "productTitle": "小说",
                    "artifactTitle": "第一章",
                    "artifactKind": "chapter",
                    "content": "正文。",
                    "summary": "第一章。"
                  }
                }
                """
            )

        self.assertEqual(error.exception.code, "tool_action_schema_invalid")

    def test_rejects_inspect_without_product_or_artifact_ids(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                {
                  "tool": "inspect_product",
                  "arguments": {
                    "reason": "查看内容。",
                    "productIds": [],
                    "artifactIds": [],
                    "focus": "全部"
                  }
                }
                """
            )

        self.assertEqual(error.exception.code, "tool_action_schema_invalid")

    def test_parses_valid_review_product_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "review_product",
              "arguments": {
                "reason": "终稿前需要审核。",
                "productIds": ["product_1"],
                "artifactIds": ["artifact_1"],
                "reviewTitle": "长篇小说审核",
                "reviewProfile": "long_form_novel_v1",
                "verdict": "needs_revision",
                "score": 76,
                "summary": "长度接近要求，但第二章衔接需要加强。",
                "findings": [
                  {
                    "severity": "major",
                    "area": "structure",
                    "claim": "第二章转折过快。",
                    "evidence": "第二章摘要缺少父亲线索。",
                    "requiredChange": "补足线索过渡。"
                  }
                ],
                "passedChecks": ["has_outline_artifact"],
                "recommendedNextTool": "discuss_with_delegate"
              }
            }
            """
        )

        self.assertEqual(action.tool, "review_product")
        self.assertEqual(action.arguments.verdict, "needs_revision")
        self.assertEqual(action.arguments.findings[0].severity, "major")

    def test_parses_valid_discuss_with_delegate_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "discuss_with_delegate",
              "arguments": {
                "reason": "需要和章节作者确认修订方向。",
                "agentSlot": "agent_2",
                "discussionTitle": "第二章修订讨论",
                "windowId": "window_1",
                "productId": "product_1",
                "artifactIds": ["artifact_2"],
                "question": "第二章怎样补足父亲线索？",
                "expectedOutcome": "给出三条可执行修订建议。",
                "maxTurns": 1
              }
            }
            """
        )

        self.assertEqual(action.tool, "discuss_with_delegate")
        self.assertEqual(action.arguments.agent_slot, "agent_2")
        self.assertEqual(action.arguments.max_turns, 1)

    def test_rejects_discussion_without_source_binding(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                {
                  "tool": "discuss_with_delegate",
                  "arguments": {
                    "reason": "泛泛讨论。",
                    "agentSlot": "agent_2",
                    "discussionTitle": "讨论",
                    "windowId": null,
                    "productId": null,
                    "artifactIds": [],
                    "question": "你怎么看？",
                    "expectedOutcome": "建议。",
                    "maxTurns": 1
                  }
                }
                """
            )

        self.assertEqual(error.exception.code, "tool_action_schema_invalid")

    def test_parses_valid_web_search_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "web_search",
              "arguments": {
                "reason": "需要查找最新资料。",
                "query": "2026 Chinese science fiction award winners",
                "searchType": "reference",
                "maxResults": 5,
                "recencyDays": 30,
                "allowedDomains": ["example.com"],
                "blockedDomains": []
              }
            }
            """
        )

        self.assertEqual(action.tool, "web_search")
        self.assertEqual(action.arguments.query, "2026 Chinese science fiction award winners")
        self.assertEqual(action.arguments.max_results, 5)
        self.assertEqual(action.arguments.allowed_domains, ["example.com"])

    def test_parses_valid_evaluate_product_action(self) -> None:
        action = parse_tool_action(
            """
            {
              "tool": "evaluate_product",
              "arguments": {
                "reason": "终稿前需要可靠性检查。",
                "profile": "research_reliability_v1",
                "productIds": ["product_1"],
                "artifactIds": ["artifact_1"],
                "focus": "检查论文最终稿和来源证据。"
              }
            }
            """
        )

        self.assertEqual(action.tool, "evaluate_product")
        self.assertEqual(action.arguments.profile, "research_reliability_v1")
        self.assertEqual(action.arguments.product_ids, ["product_1"])
        self.assertEqual(action.arguments.artifact_ids, ["artifact_1"])

    def test_rejects_web_search_over_result_limit(self) -> None:
        with self.assertRaises(ToolActionValidationError) as error:
            parse_tool_action(
                """
                {
                  "tool": "web_search",
                  "arguments": {
                    "reason": "搜索过多结果。",
                    "query": "latest AI news",
                    "searchType": "news",
                    "maxResults": 20,
                    "recencyDays": 7,
                    "allowedDomains": [],
                    "blockedDomains": []
                  }
                }
                """
            )

        self.assertEqual(error.exception.code, "tool_action_schema_invalid")
