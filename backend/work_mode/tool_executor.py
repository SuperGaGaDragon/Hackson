"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

import json
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from work_mode.action_client import ToolActionClientError
from work_mode.context import build_delegate_context
from work_mode.evaluator import (
    EvaluatorRuntime,
    artifact_is_research_paper_final_draft,
    is_research_paper_like_goal,
)
from work_mode.quality_checks import validate_final_product_quality
from work_mode.search import SearchProviderError
from work_mode.service import WorkModeService
from work_mode.tool_protocol import (
    AskUserArguments,
    BlockMissionArguments,
    DelegateAgentArguments,
    DiscussWithDelegateArguments,
    EvaluateProductArguments,
    FinishMissionArguments,
    InspectProductArguments,
    MissionPlanArguments,
    ReviewProductArguments,
    ToolAction,
    WebSearchArguments,
    WorkProductArguments,
)


class ToolExecutionResult:
    """Result returned to the Mission loop after one validated tool action."""

    def __init__(
        self,
        observation: dict[str, Any],
        terminal: bool = False,
        product_id: str | None = None,
        artifact_id: str | None = None,
    ):
        self.observation = observation
        self.terminal = terminal
        self.product_id = product_id
        self.artifact_id = artifact_id


class DelegateClientProtocol(Protocol):
    def generate_delegate_result(self, context: dict[str, Any]) -> str | dict[str, Any]: ...


class SearchProviderProtocol(Protocol):
    def search(self, request: dict[str, Any]) -> dict[str, Any]: ...


class DelegateResult(BaseModel):
    status: str = Field(pattern="^(completed|blocked)$")
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=1000)
    content: str = Field(default="")
    reason: str = Field(min_length=1, max_length=240)
    structured: bool = Field(default=True, exclude=True)

    model_config = ConfigDict(populate_by_name=True)


class DiscussionTranscriptTurn(BaseModel):
    speaker: str = Field(pattern="^(lead|delegate)$")
    content: str = Field(min_length=1, max_length=4000)


class DiscussionResult(BaseModel):
    status: str = Field(pattern="^(completed|blocked)$")
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=1000)
    transcript: list[DiscussionTranscriptTurn] = Field(default_factory=list, max_length=12)
    recommendation: str = Field(default="", max_length=2000)
    reason: str = Field(min_length=1, max_length=240)
    structured: bool = Field(default=True, exclude=True)

    model_config = ConfigDict(populate_by_name=True)


class WebSearchResultItem(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    url: str = Field(min_length=1, max_length=2000)
    source: str = Field(default="", max_length=200)
    snippet: str = Field(default="", max_length=1200)
    published_at: str | None = Field(default=None, alias="publishedAt")

    model_config = ConfigDict(populate_by_name=True)


class WebSearchProviderResult(BaseModel):
    status: str = Field(pattern="^(ok|failed)$")
    results: list[WebSearchResultItem] = Field(default_factory=list, max_length=10)
    truncated: bool = False
    provider: str = Field(default="unknown", max_length=120)
    query: str | None = Field(default=None, max_length=500)
    effective_query: str | None = Field(default=None, max_length=500, alias="effectiveQuery")
    fallback_applied: bool = Field(default=False, alias="fallbackApplied")
    fallback_reason: str | None = Field(default=None, max_length=120, alias="fallbackReason")
    attempt_count: int = Field(default=1, ge=1, le=5, alias="attemptCount")
    code: str | None = Field(default=None, max_length=120)
    retryable: bool = False

    model_config = ConfigDict(populate_by_name=True)


class WorkModeToolExecutor:
    """Execute V1.0 database-only Work Mode tools."""

    def __init__(
        self,
        service: WorkModeService,
        delegate_client: DelegateClientProtocol | None = None,
        search_provider: SearchProviderProtocol | None = None,
    ):
        self.service = service
        self.delegate_client = delegate_client
        self.search_provider = search_provider

    def execute(self, user_id: str, mission_id: str, run_id: str, action: ToolAction) -> ToolExecutionResult:
        if action.tool == "mission_plan":
            return self._mission_plan(user_id, mission_id, run_id, action.arguments)
        if action.tool == "work_product":
            return self._work_product(user_id, mission_id, run_id, action.arguments)
        if action.tool == "inspect_product":
            return self._inspect_product(user_id, mission_id, run_id, action.arguments)
        if action.tool == "delegate_agent":
            return self._delegate_agent(user_id, mission_id, run_id, action.arguments)
        if action.tool == "ask_user":
            return self._ask_user(user_id, mission_id, run_id, action.arguments)
        if action.tool == "finish_mission":
            return self._finish_mission(user_id, mission_id, run_id, action.arguments)
        if action.tool == "block_mission":
            return self._block_mission(user_id, mission_id, run_id, action.arguments)
        if action.tool == "review_product":
            return self._review_product(user_id, mission_id, run_id, action.arguments)
        if action.tool == "discuss_with_delegate":
            return self._discuss_with_delegate(user_id, mission_id, run_id, action.arguments)
        if action.tool == "web_search":
            return self._web_search(user_id, mission_id, run_id, action.arguments)
        if action.tool == "evaluate_product":
            return self._evaluate_product(user_id, mission_id, run_id, action.arguments)
        return ToolExecutionResult(
            {"tool": action.tool, "status": "unsupported", "message": "tool_not_implemented"},
            terminal=True,
        )

    def _mission_plan(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: MissionPlanArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        run = {"_id": run_id}
        payload = {
            "reason": arguments.reason,
            "planTitle": arguments.plan_title,
            "steps": [step.model_dump() for step in arguments.steps],
            "employee": _employee_payload(mission),
        }
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="MISSION_PLAN_UPDATED",
            title=arguments.plan_title,
            message=arguments.reason,
            payload=payload,
        )
        return ToolExecutionResult({"tool": "mission_plan", "status": "ok", "planTitle": arguments.plan_title})

    def _work_product(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: WorkProductArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        run = {"_id": run_id}
        employee = _employee_payload(mission)
        product_id = arguments.product_id
        if arguments.operation == "create_product":
            product = self.service.create_product(
                user_id,
                mission_id,
                title=arguments.product_title,
                summary=arguments.summary,
                created_by=employee,
            )
            product_id = product["id"]
        artifact = self.service.create_product_artifact(
            user_id,
            mission_id,
            run_id,
            product_id or "",
            kind=arguments.artifact_kind,
            title=arguments.artifact_title,
            content=arguments.content,
            summary=arguments.summary,
            created_by=employee,
            source_artifact_ids=arguments.source_artifact_ids,
            work_window_id=None,
            metadata={"summary": arguments.summary, "operation": arguments.operation},
        )
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="PRODUCT_UPDATED",
            title=arguments.artifact_title,
            message=arguments.summary,
            payload={
                "reason": arguments.reason,
                "productId": product_id,
                "artifactId": artifact["id"],
                "kind": arguments.artifact_kind,
                "summary": arguments.summary,
                "employee": employee,
            },
        )
        return ToolExecutionResult(
            {"tool": "work_product", "status": "ok", "productId": product_id, "artifactId": artifact["id"]},
            product_id=product_id,
            artifact_id=artifact["id"],
        )

    def _inspect_product(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: InspectProductArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        run = {"_id": run_id}
        detail = self.service.get_mission_detail(user_id, mission_id)
        product_ids = set(arguments.product_ids)
        artifact_ids = set(arguments.artifact_ids)
        product_artifact_ids = {
            artifact_id
            for product in detail["products"]
            if product["id"] in product_ids
            for artifact_id in product.get("artifactIds", [])
        }
        artifact_ids.update(product_artifact_ids)
        inspected = [
            {
                "id": artifact["id"],
                "title": artifact["title"],
                "kind": artifact["kind"],
                "summary": artifact.get("metadata", {}).get("summary", ""),
                "excerpt": artifact["content"][:2400],
            }
            for artifact in detail["artifacts"]
            if artifact["id"] in artifact_ids
        ][:6]
        payload = {
            "reason": arguments.reason,
            "productIds": arguments.product_ids,
            "artifactIds": [artifact["id"] for artifact in inspected],
            "focus": arguments.focus,
            "inspected": inspected,
            "employee": _employee_payload(mission),
        }
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="PRODUCT_INSPECTED",
            title="Product inspected",
            message=arguments.focus or arguments.reason,
            payload=payload,
        )
        return ToolExecutionResult({"tool": "inspect_product", "status": "ok", "inspected": inspected})

    def _delegate_agent(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: DelegateAgentArguments,
    ) -> ToolExecutionResult:
        if self.delegate_client is None:
            return ToolExecutionResult(
                {"tool": "delegate_agent", "status": "error", "message": "delegate_client_unavailable"},
                terminal=True,
            )
        mission = self.service._require_mission(user_id, mission_id)
        lead = _employee_payload(mission)
        if arguments.agent_slot == lead["id"]:
            return ToolExecutionResult(
                {"tool": "delegate_agent", "status": "error", "message": "delegate_target_must_be_non_lead"},
                terminal=True,
            )
        run = {"_id": run_id}
        window = self.service.create_work_window(
            user_id,
            mission_id,
            run_id,
            agent_slot=arguments.agent_slot,
            title=arguments.window_title,
            brief=arguments.brief,
            metadata={
                "reason": arguments.reason,
                "expectedOutput": arguments.expected_output,
                "targetProductId": arguments.target_product_id,
                "sourceArtifactIds": arguments.source_artifact_ids,
            },
        )
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="WORK_WINDOW_OPENED",
            title=arguments.window_title,
            message=arguments.reason,
            payload={"windowId": window["id"], "agentSlot": arguments.agent_slot, "employee": lead},
        )
        detail = self.service.get_mission_detail(user_id, mission_id)
        target_product = _find_public_product(detail["products"], arguments.target_product_id)
        source_artifacts = _find_public_artifacts(detail["artifacts"], arguments.source_artifact_ids)
        delegate_context = build_delegate_context(
            mission=detail["mission"],
            delegate_agent=_delegate_agent_payload(arguments.agent_slot),
            brief=arguments.brief,
            expected_output=arguments.expected_output,
            target_product=target_product,
            source_artifacts=source_artifacts,
        )
        try:
            delegate_result = _parse_delegate_result(
                self.delegate_client.generate_delegate_result(delegate_context),
                fallback_title=arguments.window_title,
                fallback_reason=arguments.reason,
            )
        except ToolActionClientError as exc:
            failed_window = self.service.mark_work_window_failed(user_id, window["id"], exc.code)
            self.service.append_event(
                user_id,
                mission,
                run=run,
                step=None,
                event_type="WORK_WINDOW_FAILED",
                title="Window failed",
                message=exc.code,
                payload={"windowId": failed_window["id"], "error": exc.code, "employee": lead},
            )
            raise
        except ValueError as exc:
            failed_window = self.service.mark_work_window_failed(user_id, window["id"], "delegate_result_invalid")
            self.service.append_event(
                user_id,
                mission,
                run=run,
                step=None,
                event_type="WORK_WINDOW_FAILED",
                title="Window failed",
                message="delegate_result_invalid",
                payload={
                    "windowId": failed_window["id"],
                    "error": "delegate_result_invalid",
                    "retryable": True,
                    "employee": lead,
                },
            )
            raise ToolActionClientError("delegate_result_invalid", "delegate_result_invalid", retryable=True) from exc
        if delegate_result.status == "blocked":
            blocked_window = self.service.mark_work_window_blocked(user_id, window["id"], delegate_result.summary)
            self.service.append_event(
                user_id,
                mission,
                run=run,
                step=None,
                event_type="WORK_WINDOW_BLOCKED",
                title=delegate_result.title,
                message=delegate_result.summary,
                payload={"windowId": blocked_window["id"], "reason": delegate_result.reason, "employee": lead},
            )
            return ToolExecutionResult(
                {
                    "tool": "delegate_agent",
                    "status": "blocked",
                    "windowId": blocked_window["id"],
                    "summary": delegate_result.summary,
                }
            )
        product_id = arguments.target_product_id
        if product_id is None:
            product = self.service.create_product(
                user_id,
                mission_id,
                title=delegate_result.title,
                summary=delegate_result.summary,
                created_by=_delegate_agent_payload(arguments.agent_slot),
            )
            product_id = product["id"]
        artifact = self.service.create_product_artifact(
            user_id,
            mission_id,
            run_id,
            product_id,
            kind=_artifact_kind_for_delegate(arguments.expected_output),
            title=delegate_result.title,
            content=delegate_result.content,
            summary=delegate_result.summary,
            created_by=_delegate_agent_payload(arguments.agent_slot),
            source_artifact_ids=arguments.source_artifact_ids,
            work_window_id=window["id"],
            metadata={
                "summary": delegate_result.summary,
                "delegateReason": delegate_result.reason,
                "delegateStructured": delegate_result.structured,
            },
        )
        completed_window = self.service.complete_work_window(
            user_id,
            window["id"],
            result_artifact_id=artifact["id"],
            summary=delegate_result.summary,
        )
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="WORK_WINDOW_COMPLETED",
            title=delegate_result.title,
            message=delegate_result.summary,
            payload={
                "windowId": completed_window["id"],
                "artifactId": artifact["id"],
                "productId": product_id,
                "agentSlot": arguments.agent_slot,
                "employee": lead,
            },
        )
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="PRODUCT_UPDATED",
            title=delegate_result.title,
            message=delegate_result.summary,
            payload={
                "reason": arguments.reason,
                "productId": product_id,
                "artifactId": artifact["id"],
                "kind": artifact["kind"],
                "summary": delegate_result.summary,
                "windowId": completed_window["id"],
                "employee": lead,
            },
        )
        return ToolExecutionResult(
            {
                "tool": "delegate_agent",
                "status": "ok",
                "windowId": completed_window["id"],
                "productId": product_id,
                "artifactId": artifact["id"],
                "summary": delegate_result.summary,
            },
            product_id=product_id,
            artifact_id=artifact["id"],
        )

    def _ask_user(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: AskUserArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        mission = self.service.mark_mission_waiting_input(user_id, mission_id, arguments.question, run_id=run_id)
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type="USER_INPUT_REQUESTED",
            title="Input requested",
            message=arguments.question,
            payload={
                "reason": arguments.reason,
                "question": arguments.question,
                "suggestedOptions": arguments.suggested_options,
                "employee": _employee_payload(mission),
            },
        )
        return ToolExecutionResult(
            {"tool": "ask_user", "status": "waiting_input", "question": arguments.question},
            terminal=True,
        )

    def _finish_mission(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: FinishMissionArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        final_products = []
        for product_id in arguments.final_product_ids:
            final_products.append(self.service.repository.find_product(product_id, user_id))
        if any(product is None or str(product["mission_id"]) != str(mission["_id"]) for product in final_products):
            raise _http_not_found("product_not_found")
        for artifact_id in arguments.final_artifact_ids:
            self.service.require_artifact(user_id, mission_id, artifact_id)
        detail = self.service.get_mission_detail(user_id, mission_id)
        quality = validate_final_product_quality(
            mission,
            detail,
            arguments.final_product_ids,
            arguments.final_artifact_ids,
        )
        if is_research_paper_like_goal(f"{mission.get('title', '')} {mission.get('goal', '')}"):
            _validate_research_paper_completion(detail, arguments.final_product_ids, arguments.final_artifact_ids)
        for product_id in arguments.final_product_ids:
            self.service.mark_product_final(user_id, product_id)
        self.service.mark_mission_completed(
            user_id,
            mission_id,
            run_id,
            step_id=None,
            final_product_ids=arguments.final_product_ids,
            final_artifact_ids=arguments.final_artifact_ids,
            summary=arguments.summary,
        )
        return ToolExecutionResult(
            {
                "tool": "finish_mission",
                "status": "ok",
                "summary": arguments.summary,
                "finalProductIds": arguments.final_product_ids,
                "finalArtifactIds": arguments.final_artifact_ids,
                "missionStatus": "completed",
                "quality": quality,
                "employee": _employee_payload(mission),
            },
            terminal=True,
        )

    def _evaluate_product(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: EvaluateProductArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        detail = self.service.get_mission_detail(user_id, mission_id)
        _require_public_products(detail["products"], arguments.product_ids)
        _require_public_artifacts_by_ids(detail["artifacts"], arguments.artifact_ids)
        evaluated = EvaluatorRuntime(self.service).evaluate(user_id, mission_id, profile=arguments.profile)
        report = _latest_reliability_report(evaluated)
        observation = {
            "tool": "evaluate_product",
            "status": "ok",
            "profile": arguments.profile,
            "score": report.get("score"),
            "reliabilityStatus": report.get("status"),
            "issueCounts": report.get("issueCounts", {}),
            "reportArtifactId": report.get("reportArtifactId"),
            "topIssues": _top_reliability_issues(report),
            "recommendedNextTool": _recommended_next_tool(report),
            "summary": report.get("summary", ""),
        }
        return ToolExecutionResult(
            {**observation, "employee": _employee_payload(mission)},
            artifact_id=report.get("reportArtifactId"),
        )

    def _block_mission(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: BlockMissionArguments,
    ) -> ToolExecutionResult:
        mission, run = self.service.mark_mission_blocked(user_id, mission_id, run_id, arguments.blocked_reason)
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="MISSION_BLOCKED",
            title="Blocked",
            message=arguments.blocked_reason,
            payload={
                "reason": arguments.reason,
                "blockedReason": arguments.blocked_reason,
                "neededFromUser": arguments.needed_from_user,
                "employee": _employee_payload(mission),
            },
        )
        return ToolExecutionResult(
            {"tool": "block_mission", "status": "blocked", "blockedReason": arguments.blocked_reason},
            terminal=True,
        )

    def _review_product(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: ReviewProductArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        run = {"_id": run_id}
        detail = self.service.get_mission_detail(user_id, mission_id)
        product_ids = _require_public_products(detail["products"], arguments.product_ids)
        artifact_ids = _require_public_artifacts_by_ids(detail["artifacts"], arguments.artifact_ids)
        if not artifact_ids:
            artifact_ids = [
                artifact_id
                for product in detail["products"]
                if product["id"] in product_ids
                for artifact_id in product.get("artifactIds", [])
            ]
        primary_product_id = product_ids[0] if product_ids else _product_id_for_artifact(detail, artifact_ids[0])
        content = _review_content(arguments)
        artifact = self.service.create_product_artifact(
            user_id,
            mission_id,
            run_id,
            primary_product_id,
            kind="report",
            title=arguments.review_title,
            content=content,
            summary=arguments.summary,
            created_by=_employee_payload(mission),
            source_artifact_ids=artifact_ids,
            work_window_id=None,
            metadata={
                "summary": arguments.summary,
                "artifactRole": "review",
                "reviewProfile": arguments.review_profile,
                "verdict": arguments.verdict,
                "score": arguments.score,
                "findings": [finding.model_dump(by_alias=True) for finding in arguments.findings],
                "passedChecks": arguments.passed_checks,
                "recommendedNextTool": arguments.recommended_next_tool,
            },
        )
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="PRODUCT_REVIEWED",
            title=arguments.review_title,
            message=arguments.summary,
            payload={
                "reason": arguments.reason,
                "productIds": product_ids,
                "artifactIds": artifact_ids,
                "reviewArtifactId": artifact["id"],
                "verdict": arguments.verdict,
                "score": arguments.score,
                "findings": [finding.model_dump(by_alias=True) for finding in arguments.findings],
                "recommendedNextTool": arguments.recommended_next_tool,
                "employee": _employee_payload(mission),
            },
        )
        return ToolExecutionResult(
            {
                "tool": "review_product",
                "status": "ok",
                "reviewArtifactId": artifact["id"],
                "verdict": arguments.verdict,
                "score": arguments.score,
                "summary": arguments.summary,
            },
            artifact_id=artifact["id"],
            product_id=primary_product_id,
        )

    def _discuss_with_delegate(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: DiscussWithDelegateArguments,
    ) -> ToolExecutionResult:
        if self.delegate_client is None:
            return ToolExecutionResult(
                {"tool": "discuss_with_delegate", "status": "error", "message": "delegate_client_unavailable"},
                terminal=True,
            )
        mission = self.service._require_mission(user_id, mission_id)
        lead = _employee_payload(mission)
        if arguments.agent_slot == lead["id"]:
            return ToolExecutionResult(
                {"tool": "discuss_with_delegate", "status": "error", "message": "delegate_target_must_be_non_lead"},
                terminal=True,
            )
        detail = self.service.get_mission_detail(user_id, mission_id)
        product_id = _require_optional_product(detail["products"], arguments.product_id)
        artifact_ids = _require_public_artifacts_by_ids(detail["artifacts"], arguments.artifact_ids)
        if product_id is None and artifact_ids:
            product_id = _product_id_for_artifact(detail, artifact_ids[0])
        window = self.service.create_work_window(
            user_id,
            mission_id,
            run_id,
            agent_slot=arguments.agent_slot,
            title=arguments.discussion_title,
            brief=arguments.question,
            metadata={
                "windowType": "discussion",
                "reason": arguments.reason,
                "sourceWindowId": arguments.window_id,
                "productId": product_id,
                "sourceArtifactIds": artifact_ids,
                "expectedOutcome": arguments.expected_outcome,
                "maxTurns": arguments.max_turns,
            },
        )
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type="DISCUSSION_WINDOW_OPENED",
            title=arguments.discussion_title,
            message=arguments.question,
            payload={"windowId": window["id"], "agentSlot": arguments.agent_slot, "employee": lead},
        )
        discussion_context = {
            "mission": detail["mission"],
            "delegateAgent": _delegate_agent_payload(arguments.agent_slot),
            "discussionTitle": arguments.discussion_title,
            "question": arguments.question,
            "expectedOutcome": arguments.expected_outcome,
            "maxTurns": arguments.max_turns,
            "sourceWindowId": arguments.window_id,
            "targetProduct": _find_public_product(detail["products"], product_id),
            "sourceArtifacts": _find_public_artifacts(detail["artifacts"], artifact_ids),
            "responseContract": (
                "Return structured discussion JSON with status, title, summary, transcript, recommendation, and reason. "
                "Do not modify product content or finish the mission."
            ),
        }
        try:
            discussion_result = _parse_discussion_result(
                self.delegate_client.generate_delegate_result(discussion_context),
                fallback_title=arguments.discussion_title,
                fallback_reason=arguments.reason,
            )
        except ToolActionClientError as exc:
            failed_window = self.service.mark_work_window_failed(user_id, window["id"], exc.code)
            self.service.append_event(
                user_id,
                mission,
                run={"_id": run_id},
                step=None,
                event_type="DISCUSSION_WINDOW_FAILED",
                title="Discussion failed",
                message=exc.code,
                payload={"windowId": failed_window["id"], "error": exc.code, "employee": lead},
            )
            raise
        except ValueError as exc:
            failed_window = self.service.mark_work_window_failed(user_id, window["id"], "discussion_result_invalid")
            self.service.append_event(
                user_id,
                mission,
                run={"_id": run_id},
                step=None,
                event_type="DISCUSSION_WINDOW_FAILED",
                title="Discussion failed",
                message="discussion_result_invalid",
                payload={"windowId": failed_window["id"], "error": "discussion_result_invalid", "employee": lead},
            )
            raise ToolActionClientError("discussion_result_invalid", "discussion_result_invalid", retryable=True) from exc
        if discussion_result.status == "blocked":
            blocked_window = self.service.mark_work_window_blocked(user_id, window["id"], discussion_result.summary)
            self.service.append_event(
                user_id,
                mission,
                run={"_id": run_id},
                step=None,
                event_type="DISCUSSION_WINDOW_BLOCKED",
                title=discussion_result.title,
                message=discussion_result.summary,
                payload={"windowId": blocked_window["id"], "reason": discussion_result.reason, "employee": lead},
            )
            return ToolExecutionResult(
                {
                    "tool": "discuss_with_delegate",
                    "status": "blocked",
                    "windowId": blocked_window["id"],
                    "summary": discussion_result.summary,
                }
            )
        if product_id is None:
            product = self.service.create_product(
                user_id,
                mission_id,
                title=discussion_result.title,
                summary=discussion_result.summary,
                created_by=_delegate_agent_payload(arguments.agent_slot),
                metadata={"artifactRole": "discussion"},
            )
            product_id = product["id"]
        artifact = self.service.create_product_artifact(
            user_id,
            mission_id,
            run_id,
            product_id,
            kind="notes",
            title=discussion_result.title,
            content=_discussion_content(discussion_result),
            summary=discussion_result.summary,
            created_by=_delegate_agent_payload(arguments.agent_slot),
            source_artifact_ids=artifact_ids,
            work_window_id=window["id"],
            metadata={
                "summary": discussion_result.summary,
                "artifactRole": "discussion",
                "sourceWindowId": arguments.window_id,
                "recommendation": discussion_result.recommendation,
                "transcript": [turn.model_dump() for turn in discussion_result.transcript],
            },
        )
        completed_window = self.service.complete_work_window(
            user_id,
            window["id"],
            result_artifact_id=artifact["id"],
            summary=discussion_result.summary,
        )
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type="DISCUSSION_WINDOW_COMPLETED",
            title=discussion_result.title,
            message=discussion_result.summary,
            payload={
                "windowId": completed_window["id"],
                "artifactId": artifact["id"],
                "productId": product_id,
                "recommendation": discussion_result.recommendation,
                "employee": lead,
            },
        )
        return ToolExecutionResult(
            {
                "tool": "discuss_with_delegate",
                "status": "ok",
                "windowId": completed_window["id"],
                "discussionArtifactId": artifact["id"],
                "summary": discussion_result.summary,
                "recommendation": discussion_result.recommendation,
            },
            product_id=product_id,
            artifact_id=artifact["id"],
        )

    def _web_search(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        arguments: WebSearchArguments,
    ) -> ToolExecutionResult:
        mission = self.service._require_mission(user_id, mission_id)
        request = {
            "query": arguments.query,
            "searchType": arguments.search_type,
            "maxResults": arguments.max_results,
            "recencyDays": arguments.recency_days,
            "allowedDomains": arguments.allowed_domains,
            "blockedDomains": arguments.blocked_domains,
        }
        if self.search_provider is None:
            observation = {
                "tool": "web_search",
                "status": "failed",
                "code": "search_provider_unavailable",
                "query": arguments.query,
                "retryable": False,
            }
            self.service.append_event(
                user_id,
                mission,
                run={"_id": run_id},
                step=None,
                event_type="WEB_SEARCH_FAILED",
                title="Search failed",
                message="search_provider_unavailable",
                payload={**observation, "reason": arguments.reason, "employee": _employee_payload(mission)},
            )
            return ToolExecutionResult(observation)
        try:
            provider_result = _parse_search_provider_result(self.search_provider.search(request))
        except SearchProviderError as exc:
            provider_result = WebSearchProviderResult(
                status="failed",
                results=[],
                truncated=False,
                provider=self.search_provider.__class__.__name__,
                query=arguments.query,
                effectiveQuery=arguments.query,
                code=exc.code,
                retryable=exc.retryable,
            )
        if provider_result.status == "failed":
            code = provider_result.code or "search_provider_unavailable"
            observation = {
                "tool": "web_search",
                "status": "failed",
                "code": code,
                "query": arguments.query,
                "effectiveQuery": provider_result.effective_query or arguments.query,
                "fallbackApplied": provider_result.fallback_applied,
                "fallbackReason": provider_result.fallback_reason,
                "attemptCount": provider_result.attempt_count,
                "retryable": provider_result.retryable,
                "provider": provider_result.provider,
            }
            self.service.append_event(
                user_id,
                mission,
                run={"_id": run_id},
                step=None,
                event_type="WEB_SEARCH_FAILED",
                title="Search failed",
                message=code,
                payload={**observation, "reason": arguments.reason, "employee": _employee_payload(mission)},
            )
            return ToolExecutionResult(observation)

        results = [item.model_dump(by_alias=True) for item in provider_result.results[: arguments.max_results]]
        observation = {
            "tool": "web_search",
            "status": "ok",
            "query": arguments.query,
            "effectiveQuery": provider_result.effective_query or provider_result.query or arguments.query,
            "searchType": arguments.search_type,
            "results": results,
            "truncated": provider_result.truncated or len(provider_result.results) > arguments.max_results,
            "provider": provider_result.provider,
            "fallbackApplied": provider_result.fallback_applied,
            "fallbackReason": provider_result.fallback_reason,
            "attemptCount": provider_result.attempt_count,
        }
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type="WEB_SEARCH_COMPLETED",
            title="Search",
            message=arguments.query,
            payload={**observation, "reason": arguments.reason, "employee": _employee_payload(mission)},
        )
        return ToolExecutionResult(observation)


def _employee_payload(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission.get("lead_employee_id", "employee_default_lead"),
        "name": mission.get("lead_employee_name", "Lead"),
        "role": mission.get("lead_employee_role", "Mission lead"),
    }


def _http_not_found(detail: str):
    from fastapi import HTTPException, status

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _delegate_agent_payload(agent_slot: str) -> dict[str, str]:
    label = "Agent 1" if agent_slot == "agent_1" else "Agent 2"
    return {"id": agent_slot, "name": label, "role": "Delegate Agent"}


def _artifact_kind_for_delegate(expected_output: str) -> str:
    if expected_output in {"outline", "chapter", "revision", "summary"}:
        return "notes" if expected_output == "summary" else expected_output
    if expected_output == "review":
        return "report"
    return "other"


def _find_public_product(products: list[dict[str, Any]], product_id: str | None) -> dict[str, Any] | None:
    if product_id is None:
        return None
    return next((product for product in products if product["id"] == product_id), None)


def _find_public_artifacts(artifacts: list[dict[str, Any]], artifact_ids: list[str]) -> list[dict[str, Any]]:
    wanted = set(artifact_ids)
    return [artifact for artifact in artifacts if artifact["id"] in wanted]


def _require_public_products(products: list[dict[str, Any]], product_ids: list[str]) -> list[str]:
    available = {product["id"] for product in products}
    missing = [product_id for product_id in product_ids if product_id not in available]
    if missing:
        raise _http_not_found("product_not_found")
    return product_ids


def _require_optional_product(products: list[dict[str, Any]], product_id: str | None) -> str | None:
    if product_id is None:
        return None
    _require_public_products(products, [product_id])
    return product_id


def _require_public_artifacts_by_ids(artifacts: list[dict[str, Any]], artifact_ids: list[str]) -> list[str]:
    available = {artifact["id"] for artifact in artifacts}
    missing = [artifact_id for artifact_id in artifact_ids if artifact_id not in available]
    if missing:
        raise _http_not_found("artifact_not_found")
    return artifact_ids


def _product_id_for_artifact(detail: dict[str, Any], artifact_id: str) -> str:
    artifact = next((item for item in detail["artifacts"] if item["id"] == artifact_id), None)
    product_id = artifact.get("metadata", {}).get("productId") if artifact else None
    if product_id:
        return product_id
    for product in detail["products"]:
        if artifact_id in product.get("artifactIds", []):
            return product["id"]
    raise _http_not_found("product_not_found")


def _validate_research_paper_completion(
    detail: dict[str, Any],
    final_product_ids: list[str],
    final_artifact_ids: list[str],
) -> None:
    from fastapi import HTTPException, status

    if not final_artifact_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="final_paper_draft_required")
    products = [product for product in detail["products"] if product["id"] in set(final_product_ids)]
    product_artifact_ids = {
        artifact_id
        for product in products
        for artifact_id in product.get("artifactIds", [])
    }
    final_artifacts = [
        artifact
        for artifact in detail["artifacts"]
        if artifact["id"] in set(final_artifact_ids) and artifact["id"] in product_artifact_ids
    ]
    if not any(artifact_is_research_paper_final_draft(artifact) for artifact in final_artifacts):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="final_paper_draft_required")
    report = _latest_reliability_report(detail)
    if not report or not _report_is_current(detail):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="reliability_evaluation_required")
    if _report_has_blocking_issues(report):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="reliability_evaluation_needs_review")


def _latest_reliability_report(detail: dict[str, Any]) -> dict[str, Any]:
    latest_report_artifact_id = ""
    for event in reversed(detail.get("events", [])):
        if event.get("type") == "RELIABILITY_REPORTED":
            latest_report_artifact_id = str(event.get("payload", {}).get("reportArtifactId") or "")
            break
    if latest_report_artifact_id:
        artifact = next(
            (
                item
                for item in detail.get("artifacts", [])
                if item.get("id") == latest_report_artifact_id
                and item.get("metadata", {}).get("artifactRole") == "reliability_report"
            ),
            None,
        )
        report = artifact.get("metadata", {}).get("reportPayload") if artifact else None
        if isinstance(report, dict):
            return report
    reports = [
        artifact.get("metadata", {}).get("reportPayload")
        for artifact in detail.get("artifacts", [])
        if artifact.get("metadata", {}).get("artifactRole") == "reliability_report"
    ]
    reports = [report for report in reports if isinstance(report, dict)]
    if not reports:
        return {}
    return reports[-1]


def _report_has_blocking_issues(report: dict[str, Any]) -> bool:
    if report.get("status") == "unsafe_to_ship":
        return True
    issues = [issue for issue in report.get("issues", []) if isinstance(issue, dict)]
    actionable_issues = [issue for issue in issues if issue.get("type") != "mission_incomplete"]
    if not actionable_issues:
        return False
    return any(issue.get("severity") in {"critical", "high", "medium"} for issue in actionable_issues)


def _report_is_current(detail: dict[str, Any]) -> bool:
    events = detail.get("events", [])
    for event in reversed(events):
        if event.get("type") == "RELIABILITY_REPORTED":
            return True
        if event.get("type") in {"PRODUCT_UPDATED", "WORK_WINDOW_COMPLETED"}:
            return False
    return False


def _top_reliability_issues(report: dict[str, Any]) -> list[dict[str, Any]]:
    issues = report.get("issues") or []
    return [
        {
            "id": issue.get("id"),
            "type": issue.get("type"),
            "severity": issue.get("severity"),
            "title": issue.get("title"),
            "suggestedFix": issue.get("suggestedFix", ""),
        }
        for issue in issues[:4]
        if isinstance(issue, dict)
    ]


def _recommended_next_tool(report: dict[str, Any]) -> str:
    status_value = report.get("status")
    issue_types = {
        issue.get("type")
        for issue in report.get("issues", [])
        if isinstance(issue, dict)
    }
    if status_value == "ship_ready" or issue_types == {"mission_incomplete"}:
        return "finish_mission"
    if "evaluation_limitation" in issue_types or "missing_source" in issue_types:
        return "web_search"
    if "unsupported_claim" in issue_types or "weakly_supported_claim" in issue_types:
        return "work_product"
    if "missing_requirement" in issue_types:
        return "work_product"
    return "work_product"


def _review_content(arguments: ReviewProductArguments) -> str:
    findings = "\n".join(
        f"- [{finding.severity}/{finding.area}] {finding.claim} Evidence: {finding.evidence} Required: {finding.required_change}"
        for finding in arguments.findings
    )
    if not findings:
        findings = "- No findings."
    checks = ", ".join(arguments.passed_checks) if arguments.passed_checks else "none"
    return (
        f"# {arguments.review_title}\n\n"
        f"Verdict: {arguments.verdict}\n"
        f"Score: {arguments.score}\n"
        f"Profile: {arguments.review_profile}\n"
        f"Summary: {arguments.summary}\n"
        f"Passed checks: {checks}\n"
        f"Recommended next tool: {arguments.recommended_next_tool}\n\n"
        f"Findings:\n{findings}"
    )


def _parse_discussion_result(
    raw_result: str | dict[str, Any],
    fallback_title: str,
    fallback_reason: str,
) -> DiscussionResult:
    if isinstance(raw_result, dict):
        try:
            return DiscussionResult.model_validate(raw_result)
        except ValidationError as exc:
            coerced = _coerce_discussion_result_data(raw_result, fallback_title, fallback_reason)
            if coerced:
                return coerced
            raise ValueError("discussion_result_invalid") from exc

    raw_text = raw_result.strip()
    if not raw_text:
        raise ValueError("discussion_result_empty")
    for candidate in _delegate_json_candidates(raw_text):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        try:
            return DiscussionResult.model_validate(data)
        except ValidationError:
            if isinstance(data, dict):
                coerced = _coerce_discussion_result_data(data, fallback_title, fallback_reason)
                if coerced:
                    return coerced
            continue
    if _looks_like_broken_json(raw_text):
        raise ValueError("discussion_result_invalid")
    return DiscussionResult(
        status="completed",
        title=fallback_title,
        summary=_unstructured_delegate_summary(raw_text),
        transcript=[
            DiscussionTranscriptTurn(speaker="lead", content="Discussion requested."),
            DiscussionTranscriptTurn(speaker="delegate", content=_strip_markdown_fence(raw_text)),
        ],
        recommendation=_bounded_text(_strip_markdown_fence(raw_text), 2000),
        reason=fallback_reason,
        structured=False,
    )


def _coerce_discussion_result_data(
    data: dict[str, Any],
    fallback_title: str,
    fallback_reason: str,
) -> DiscussionResult | None:
    transcript = _discussion_transcript_from_data(data)
    recommendation = _discussion_recommendation_from_data(data)
    summary = _bounded_text(_string_value(data.get("summary")) or recommendation or _transcript_summary(transcript), 1000)
    status_value = data.get("status") if data.get("status") in {"completed", "blocked"} else "completed"
    if status_value == "blocked" and not summary:
        summary = _bounded_text(_string_value(data.get("reason")) or fallback_reason, 1000)
    if not summary and not recommendation and not transcript:
        return None
    if not transcript:
        transcript = [
            DiscussionTranscriptTurn(speaker="lead", content="Discussion requested."),
            DiscussionTranscriptTurn(speaker="delegate", content=recommendation or summary),
        ]
    return DiscussionResult(
        status=status_value,
        title=_bounded_text(_string_value(data.get("title")) or fallback_title, 200),
        summary=summary or _unstructured_delegate_summary(recommendation),
        transcript=transcript,
        recommendation=_bounded_text(recommendation or summary, 2000),
        reason=_bounded_text(_string_value(data.get("reason")) or fallback_reason, 240),
        structured=False,
    )


def _discussion_transcript_from_data(data: dict[str, Any]) -> list[DiscussionTranscriptTurn]:
    raw_transcript = data.get("transcript")
    turns: list[DiscussionTranscriptTurn] = []
    if isinstance(raw_transcript, list):
        for item in raw_transcript[:12]:
            if isinstance(item, dict):
                speaker = _string_value(item.get("speaker"))
                content = _string_value(item.get("content"))
                if speaker in {"lead", "delegate"} and content:
                    turns.append(DiscussionTranscriptTurn(speaker=speaker, content=_bounded_text(content, 4000)))
            elif isinstance(item, str) and item.strip():
                turns.append(DiscussionTranscriptTurn(speaker="delegate", content=_bounded_text(item, 4000)))
    elif isinstance(raw_transcript, str) and raw_transcript.strip():
        turns.append(DiscussionTranscriptTurn(speaker="delegate", content=_bounded_text(raw_transcript, 4000)))
    return turns


def _discussion_recommendation_from_data(data: dict[str, Any]) -> str:
    for key in ("recommendation", "content", "text", "result", "output", "answer", "advice"):
        value = _string_value(data.get(key))
        if value:
            return value
    text_values = [
        value.strip()
        for key, value in data.items()
        if key not in {"title", "status", "reason"}
        and isinstance(value, str)
        and value.strip()
        and len(value.strip()) > 20
    ]
    return "\n\n".join(text_values).strip()


def _transcript_summary(transcript: list[DiscussionTranscriptTurn]) -> str:
    if not transcript:
        return ""
    return _bounded_text(" ".join(turn.content for turn in transcript), 180)


def _discussion_content(result: DiscussionResult) -> str:
    transcript = "\n".join(f"{turn.speaker}: {turn.content}" for turn in result.transcript)
    return (
        f"# {result.title}\n\n"
        f"Summary: {result.summary}\n\n"
        f"Transcript:\n{transcript}\n\n"
        f"Recommendation: {result.recommendation}\n"
        f"Reason: {result.reason}"
    )


def _parse_search_provider_result(raw_result: dict[str, Any]) -> WebSearchProviderResult:
    try:
        return WebSearchProviderResult.model_validate(raw_result)
    except ValidationError as exc:
        raise ToolActionClientError("search_result_invalid", "search_result_invalid", retryable=True) from exc


def _parse_delegate_result(
    raw_result: str | dict[str, Any],
    fallback_title: str = "Delegate result",
    fallback_reason: str = "Delegate returned unstructured content.",
) -> DelegateResult:
    if isinstance(raw_result, dict):
        try:
            return DelegateResult.model_validate(raw_result)
        except ValidationError as exc:
            coerced = _coerce_delegate_result_data(raw_result, fallback_title, fallback_reason)
            if coerced:
                return coerced
            raise ValueError("delegate_result_invalid") from exc

    raw_text = raw_result.strip()
    if not raw_text:
        raise ValueError("delegate_result_empty")

    for candidate in _delegate_json_candidates(raw_text):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        try:
            return DelegateResult.model_validate(data)
        except ValidationError:
            if isinstance(data, dict):
                coerced = _coerce_delegate_result_data(data, fallback_title, fallback_reason)
                if coerced:
                    return coerced
            continue

    if _looks_like_broken_json(raw_text):
        raise ValueError("delegate_result_invalid")

    return DelegateResult(
        status="completed",
        title=fallback_title,
        summary=_unstructured_delegate_summary(raw_text),
        content=_strip_markdown_fence(raw_text),
        reason=fallback_reason,
        structured=False,
    )


def _delegate_json_candidates(raw_text: str) -> list[str]:
    candidates = [raw_text]
    fenced = _strip_markdown_fence(raw_text)
    if fenced != raw_text:
        candidates.append(fenced)
    extracted = _extract_first_json_object(raw_text)
    if extracted:
        candidates.append(extracted)
    deduped: list[str] = []
    for candidate in candidates:
        candidate = candidate.strip()
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    return deduped


def _strip_markdown_fence(raw_text: str) -> str:
    lines = raw_text.strip().splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return raw_text.strip()


def _extract_first_json_object(raw_text: str) -> str | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw_text):
        if char != "{":
            continue
        try:
            value, end = decoder.raw_decode(raw_text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return raw_text[index : index + end]
    return None


def _looks_like_broken_json(raw_text: str) -> bool:
    stripped = raw_text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return True
    first_line = stripped.splitlines()[0].strip().lower() if stripped else ""
    return first_line.startswith("```json")


def _unstructured_delegate_summary(raw_text: str) -> str:
    compact = " ".join(_strip_markdown_fence(raw_text).split())
    compact = _bounded_text(compact, 180)
    return f"已保存委派窗口返回的正文草稿：{compact}"


def _coerce_delegate_result_data(
    data: dict[str, Any],
    fallback_title: str,
    fallback_reason: str,
) -> DelegateResult | None:
    content = _delegate_content_from_data(data)
    status = data.get("status")
    if status == "blocked":
        summary = _bounded_text(_string_value(data.get("summary")) or _string_value(data.get("reason")) or content, 1000)
        if not summary:
            return None
        return DelegateResult(
            status="blocked",
            title=_bounded_text(_string_value(data.get("title")) or fallback_title, 200),
            summary=summary,
            content="",
            reason=_bounded_text(_string_value(data.get("reason")) or fallback_reason, 240),
            structured=False,
        )
    if not content:
        return None
    return DelegateResult(
        status="completed",
        title=_bounded_text(_string_value(data.get("title")) or fallback_title, 200),
        summary=_bounded_text(_string_value(data.get("summary")) or _unstructured_delegate_summary(content), 1000),
        content=content,
        reason=_bounded_text(_string_value(data.get("reason")) or fallback_reason, 240),
        structured=False,
    )


def _delegate_content_from_data(data: dict[str, Any]) -> str:
    for key in ("content", "text", "draft", "body", "chapter", "result", "output"):
        value = _string_value(data.get(key))
        if value:
            return value
    text_values = [
        value.strip()
        for value in data.values()
        if isinstance(value, str) and value.strip() and len(value.strip()) > 80
    ]
    return "\n\n".join(text_values).strip()


def _string_value(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _bounded_text(value: str, limit: int) -> str:
    value = value.strip()
    if len(value) <= limit:
        return value
    return f"{value[: max(limit - 3, 0)].rstrip()}..."
