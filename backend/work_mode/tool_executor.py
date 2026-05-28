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
from work_mode.service import WorkModeService
from work_mode.tool_protocol import (
    AskUserArguments,
    BlockMissionArguments,
    DelegateAgentArguments,
    FinishMissionArguments,
    InspectProductArguments,
    MissionPlanArguments,
    ToolAction,
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


class DelegateResult(BaseModel):
    status: str = Field(pattern="^(completed|blocked)$")
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=1000)
    content: str = Field(default="")
    reason: str = Field(min_length=1, max_length=240)
    structured: bool = Field(default=True, exclude=True)

    model_config = ConfigDict(populate_by_name=True)


class WorkModeToolExecutor:
    """Execute V1.0 database-only Work Mode tools."""

    def __init__(self, service: WorkModeService, delegate_client: DelegateClientProtocol | None = None):
        self.service = service
        self.delegate_client = delegate_client

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
        mission = self.service.mark_mission_waiting_input(user_id, mission_id, arguments.question)
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
                "employee": _employee_payload(mission),
            },
            terminal=True,
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
