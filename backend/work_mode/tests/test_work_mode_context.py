"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from unittest import TestCase

from work_mode.context import build_delegate_context, build_lead_context


class WorkModeContextTest(TestCase):
    def test_lead_context_contains_tools_manifest_windows_recent_content_and_budget(self) -> None:
        context = build_lead_context(
            mission={
                "id": "mission_1",
                "title": "写一个8000字小说",
                "goal": "写一个8000字中文小说，题材自定。",
                "status": "running",
            },
            lead_agent={"id": "agent_1", "name": "Planner", "role": "lead"},
            delegate_agent={"id": "agent_2", "name": "Writer", "role": "delegate"},
            products=[
                {
                    "id": "product_1",
                    "title": "长篇小说",
                    "status": "active",
                    "summary": "已有大纲。",
                    "artifactIds": ["artifact_1", "artifact_2", "artifact_3"],
                    "latestArtifactId": "artifact_3",
                }
            ],
            work_windows=[
                {
                    "id": "window_1",
                    "agentSlot": "agent_2",
                    "title": "第一章草稿",
                    "status": "completed",
                    "resultArtifactId": "artifact_2",
                    "summary": "完成第一章。",
                }
            ],
            events=[
                {"sequence": 1, "type": "MISSION_CREATED", "title": "Created", "message": "created", "payload": {}},
                {"sequence": 2, "type": "PRODUCT_UPDATED", "title": "Product", "message": "updated", "payload": {}},
            ],
            artifacts=[
                {
                    "id": "artifact_1",
                    "title": "大纲",
                    "kind": "outline",
                    "summary": "旧大纲",
                    "content": "旧大纲全文",
                    "metadata": {"productId": "product_1"},
                },
                {
                    "id": "artifact_2",
                    "title": "第一章",
                    "kind": "chapter",
                    "summary": "第一章摘要",
                    "content": "第一章全文",
                    "metadata": {"productId": "product_1"},
                },
                {
                    "id": "artifact_3",
                    "title": "第二章",
                    "kind": "chapter",
                    "summary": "第二章摘要",
                    "content": "第二章全文",
                    "metadata": {"productId": "product_1"},
                },
            ],
            last_observation={"tool": "work_product", "status": "ok"},
            budget={"modelTurnsUsed": 2, "modelTurnsMax": 20},
            recent_artifact_limit=2,
        )

        self.assertEqual(context["mission"]["goal"], "写一个8000字中文小说，题材自定。")
        self.assertIn("delegate_agent", context["availableTools"])
        self.assertIn("work_product", context["toolSchemas"])
        self.assertIn("finishMissionExample", context["toolExamples"])
        self.assertEqual(context["toolSchemas"]["work_product"]["arguments"]["artifactKind"], "outline|chapter|draft|revision|final|report|notes|other")
        self.assertEqual(context["productManifest"][0]["latestArtifactId"], "artifact_3")
        self.assertEqual(context["workWindowManifest"][0]["resultArtifactId"], "artifact_2")
        self.assertEqual(context["recentEvents"][-1]["type"], "PRODUCT_UPDATED")
        self.assertEqual([artifact["id"] for artifact in context["recentArtifactContent"]], ["artifact_2", "artifact_3"])
        self.assertNotIn("旧大纲全文", str(context["recentArtifactContent"]))
        self.assertEqual(context["lastObservation"]["tool"], "work_product")
        self.assertEqual(context["budget"]["modelTurnsUsed"], 2)

    def test_delegate_context_excludes_toolbox_and_scopes_brief(self) -> None:
        context = build_delegate_context(
            mission={"id": "mission_1", "title": "写小说", "goal": "写一个8000字小说"},
            delegate_agent={"id": "agent_2", "name": "Writer", "role": "delegate"},
            brief="写第一章，重点是雨夜车站。",
            expected_output="chapter",
            target_product={"id": "product_1", "title": "长篇小说", "summary": "已有大纲。"},
            source_artifacts=[
                {"id": "artifact_1", "title": "大纲", "summary": "主角寻找旧车票。", "content": "大纲全文"}
            ],
        )

        self.assertEqual(context["brief"], "写第一章，重点是雨夜车站。")
        self.assertEqual(context["delegateAgent"]["id"], "agent_2")
        self.assertEqual(context["expectedOutput"], "chapter")
        self.assertNotIn("availableTools", context)
        self.assertIn("return structured delegate result JSON", context["responseContract"])
