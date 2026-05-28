"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase

from work_mode.evaluator import EvaluatorRuntime, build_reliability_report
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
        report_event = detail["events"][-1]

        self.assertEqual(report_event["type"], "RELIABILITY_REPORTED")
        self.assertEqual(report_event["payload"]["reportArtifactId"], report_artifact["id"])
        self.assertIn("reportPayload", report_artifact["metadata"])
        self.assertEqual(report_artifact["metadata"]["reportPayload"]["reportArtifactId"], report_artifact["id"])

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
