"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from work_mode.evaluator import EVALUATOR_VERSION, EvaluatorRuntime, build_reliability_report
from work_mode.schemas import MissionCreateRequest, MissionStartRequest, ProjectCreateRequest
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository


class WorkModeEvaluatorTest(TestCase):
    def setUp(self) -> None:
        self.service = WorkModeService(FakeWorkModeRepository())

    def test_report_flags_unsupported_claim_and_ignored_search_failure(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        mission_document = self.service._require_mission("user_1", mission["id"])
        self.service.append_event(
            "user_1",
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
                "provider": "fake",
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
        self.service.append_event(
            "user_1",
            mission_document,
            run={"_id": run_id},
            step=None,
            event_type="WEB_SEARCH_FAILED",
            title="Search failed",
            message="search_timeout",
            payload={"tool": "web_search", "status": "failed", "code": "search_timeout"},
        )
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))
        issue_types = {issue.type for issue in report.issues}

        self.assertIn("unsupported_claim", issue_types)
        self.assertIn("hallucinated_entity", issue_types)
        self.assertIn("tool_failure_ignored", issue_types)
        self.assertGreaterEqual(report.issue_counts["high"], 1)
        self.assertEqual(report.issue_counts["type:tool_failure_ignored"], 1)
        self.assertEqual(report.tool_failures[0].code, "search_timeout")
        self.assertEqual(report.tool_failures[0].tool, "web_search")
        self.assertLess(report.score, 85)
        self.assertNotEqual(report.status, "ship_ready")

    def test_final_answer_text_does_not_count_as_evidence(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission(
            content=(
                "MapleNeural Labs is a Toronto-based enterprise AI company. "
                "Source: https://mapleneural.example"
            )
        )
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))
        issue_types = {issue.type for issue in report.issues}

        self.assertEqual(len(report.evidence), 0)
        self.assertIn("evaluation_limitation", issue_types)
        self.assertIn("unsupported_claim", issue_types)
        self.assertEqual(report.status, "needs_human_review")

    def test_evaluator_persists_report_artifact_and_event(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )

        detail = EvaluatorRuntime(self.service).evaluate("user_1", mission["id"])
        report_artifact = next(
            artifact for artifact in detail["artifacts"] if artifact["metadata"].get("artifactRole") == "reliability_report"
        )
        event_types = [event["type"] for event in detail["events"]]
        report_event = detail["events"][-1]

        self.assertIn("EVALUATION_STARTED", event_types)
        self.assertEqual(report_event["type"], "RELIABILITY_REPORTED")
        self.assertEqual(report_event["payload"]["reportArtifactId"], report_artifact["id"])
        self.assertEqual(report_event["payload"]["evaluatorVersion"], EVALUATOR_VERSION)
        self.assertEqual(report_event["payload"]["mode"], "live")
        self.assertEqual(report_artifact["metadata"]["evaluatorVersion"], EVALUATOR_VERSION)
        self.assertIn("reportPayload", report_artifact["metadata"])
        self.assertEqual(report_artifact["metadata"]["reportPayload"]["reportArtifactId"], report_artifact["id"])

    def test_paused_mission_is_not_ship_ready_even_with_final_artifact(self) -> None:
        mission, run_id, product, _final_artifact = self._research_mission()
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_paused_retryable(
            "user_1",
            mission["id"],
            run_id,
            "model_response_missing_text",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))
        issue_types = {issue.type for issue in report.issues}

        self.assertIn("mission_incomplete", issue_types)
        self.assertEqual(report.status, "needs_human_review")
        self.assertLess(report.score, 85)

    def test_evaluator_does_not_duplicate_current_report_without_new_trace(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )
        runtime = EvaluatorRuntime(self.service)

        first_detail = runtime.evaluate("user_1", mission["id"])
        second_detail = runtime.evaluate("user_1", mission["id"])

        first_reports = [
            artifact
            for artifact in first_detail["artifacts"]
            if artifact["metadata"].get("artifactRole") == "reliability_report"
        ]
        second_reports = [
            artifact
            for artifact in second_detail["artifacts"]
            if artifact["metadata"].get("artifactRole") == "reliability_report"
        ]
        report_events = [event for event in second_detail["events"] if event["type"] == "RELIABILITY_REPORTED"]
        started_events = [event for event in second_detail["events"] if event["type"] == "EVALUATION_STARTED"]

        self.assertEqual(len(first_reports), 1)
        self.assertEqual(len(second_reports), 1)
        self.assertEqual(len(report_events), 1)
        self.assertEqual(len(started_events), 1)

    def test_replay_mode_uses_fixture_evidence_without_mutating_search_trace(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )

        detail = EvaluatorRuntime(self.service).evaluate("user_1", mission["id"], mode="replay")
        report_artifact = next(
            artifact for artifact in detail["artifacts"] if artifact["metadata"].get("artifactRole") == "reliability_report"
        )
        report = report_artifact["metadata"]["reportPayload"]
        event_types = [event["type"] for event in detail["events"]]

        self.assertEqual(report["mode"], "replay")
        self.assertTrue(any(item["provider"] == "replay_fixture" for item in report["evidence"]))
        self.assertNotIn("WEB_SEARCH_COMPLETED", event_types)
        self.assertIn("EVALUATION_STARTED", event_types)
        self.assertIn("RELIABILITY_REPORTED", event_types)

    def test_source_backed_research_artifact_counts_as_evidence(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        self.service.create_artifact(
            "user_1",
            mission["id"],
            run_id,
            kind="notes",
            title="Cohere source note",
            content="Cohere provides enterprise AI models and is headquartered in Toronto.",
            metadata={
                "artifactRole": "research_evidence",
                "sources": [
                    {
                        "title": "Cohere enterprise AI",
                        "url": "https://cohere.com",
                        "source": "cohere.com",
                        "snippet": "Cohere provides enterprise AI models and is headquartered in Toronto.",
                    }
                ],
            },
        )
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))

        self.assertTrue(any(item.provider == "artifact" for item in report.evidence))
        self.assertFalse(
            any(issue.type == "evaluation_limitation" and issue.title == "No evidence ledger" for issue in report.issues)
        )

    def test_evaluator_emits_failed_event_when_report_cannot_be_persisted(self) -> None:
        mission, run_id, product, final_artifact = self._research_mission()
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[final_artifact["id"]],
            summary="Research complete.",
        )
        runtime = EvaluatorRuntime(self.service)

        def fail_persist(*_args, **_kwargs):
            raise RuntimeError("persist_failed")

        runtime._persist_report = fail_persist

        with self.assertRaises(RuntimeError):
            runtime.evaluate("user_1", mission["id"])

        detail = self.service.get_mission_detail("user_1", mission["id"])
        failed_event = detail["events"][-1]

        self.assertEqual(failed_event["type"], "EVALUATION_FAILED")
        self.assertEqual(failed_event["payload"]["code"], "evaluation_failed")
        self.assertEqual(failed_event["payload"]["evaluatorVersion"], EVALUATOR_VERSION)

    def test_chinese_paper_outline_only_final_is_missing_final_draft(self) -> None:
        mission, run_id, product, outline = self._paper_mission(
            kind="outline",
            title="论文大纲",
            content="一、引言。二、历史背景。三、结论。本文将讨论海地革命的原因和影响。",
        )
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[outline["id"]],
            summary="Paper complete.",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))
        missing_requirements = [
            requirement.requirement for requirement in report.requirements if requirement.status == "missing"
        ]

        self.assertIn("Produce a final paper or research draft", missing_requirements)
        self.assertEqual(report.status, "needs_human_review")

    def test_chinese_paper_final_draft_satisfies_final_draft_requirement(self) -> None:
        mission, run_id, product, artifact = self._paper_mission(
            kind="final",
            title="海地革命论文终稿",
            content=(
                "题目：海地革命的社会根源与大西洋世界影响\n\n"
                "引言：海地革命不是孤立的奴隶起义，而是法国殖民制度、种植园经济与启蒙政治语言共同作用的结果。"
                "本文认为，圣多明各被压迫群体把自由和平等的理念转化为组织行动，并最终改变了大西洋世界的权力结构。\n\n"
                "第一部分：殖民社会的结构性矛盾。圣多明各的财富建立在高度暴力化的奴隶劳动之上，"
                "白人种植园主、自由有色人和被奴役者之间的法律地位差异不断累积冲突。\n\n"
                "第二部分：革命政治语言的扩散。法国革命提供了新的合法性语言，但殖民地各阶层对自由和平等的解释并不相同，"
                "这种分歧推动了地方武装和政治联盟的重组。\n\n"
                "结论：海地革命的意义在于，它证明被压迫者并非只是欧洲政治的接受者，也能够主动重写现代自由的边界。"
            ),
        )
        self.service.mark_product_final("user_1", product["id"])
        self.service.mark_mission_completed(
            "user_1",
            mission["id"],
            run_id,
            step_id=None,
            final_product_ids=[product["id"]],
            final_artifact_ids=[artifact["id"]],
            summary="Paper complete.",
        )

        report = build_reliability_report(self.service.get_mission_detail("user_1", mission["id"]))
        final_draft = next(
            requirement for requirement in report.requirements if requirement.requirement == "Produce a final paper or research draft"
        )

        self.assertEqual(final_draft.status, "met")

    def _research_mission(self, content: str | None = None) -> tuple[dict, str, dict, dict]:
        project = self.service.create_project("user_1", ProjectCreateRequest(name="Research"))
        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title="Toronto AI research",
                goal=(
                    "Find 3 AI startups in Toronto working on enterprise AI. "
                    "For each, give one-sentence summary, source link, and personalized outreach email."
                ),
            ),
        )
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="Toronto AI outreach",
            summary="Research result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind="final",
            title="Final research",
            content=content
            or (
                "Cohere is a Toronto-based enterprise AI company. Source: https://cohere.com\n"
                "MapleNeural Labs provides enterprise AI agents to Fortune 500 banks.\n"
                "Email: Dear team, I liked your enterprise AI work."
            ),
            summary="Final research result.",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
            source_artifact_ids=[],
            work_window_id=None,
            metadata={"summary": "Final research result."},
        )
        return mission, run_id, product, artifact

    def _paper_mission(self, kind: str, title: str, content: str) -> tuple[dict, str, dict, dict]:
        project = self.service.create_project("user_1", ProjectCreateRequest(name="Paper"))
        mission = self.service.create_mission(
            "user_1",
            MissionCreateRequest(
                projectId=project["id"],
                title="海地革命论文",
                goal="写一篇关于海地革命的研究论文，需要有最终稿。",
            ),
        )
        detail = self.service.start_mission("user_1", mission["id"], MissionStartRequest())
        run_id = detail["activeRun"]["id"]
        product = self.service.create_product(
            "user_1",
            mission["id"],
            title="海地革命论文",
            summary="论文产品。",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
        )
        artifact = self.service.create_product_artifact(
            "user_1",
            mission["id"],
            run_id,
            product["id"],
            kind=kind,
            title=title,
            content=content,
            summary="论文稿。",
            created_by={"id": "agent_1", "name": "Agent 1", "role": "Lead"},
            source_artifact_ids=[],
            work_window_id=None,
            metadata={"summary": "论文稿。"},
        )
        return mission, run_id, product, artifact
