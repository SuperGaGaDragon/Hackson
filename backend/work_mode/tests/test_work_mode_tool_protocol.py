"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
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
