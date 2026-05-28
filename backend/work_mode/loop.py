"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from concurrent.futures import ThreadPoolExecutor
from time import monotonic, sleep
from typing import Any, Protocol

from fastapi import HTTPException

from work_mode.action_client import ToolActionClientError
from work_mode.context import build_lead_context
from work_mode.service import WorkModeService
from work_mode.tool_executor import ToolExecutionResult, WorkModeToolExecutor
from work_mode.tool_protocol import ToolAction


class ActionClientProtocol(Protocol):
    def generate_action(self, context: dict[str, Any]) -> ToolAction: ...


class MissionLoopRunner:
    """Run one model-driven Work Mode Mission until a terminal state."""

    def __init__(
        self,
        service: WorkModeService,
        action_client: ActionClientProtocol,
        max_turns: int = 20,
        max_invalid_turns: int = 2,
        max_retryable_turn_retries: int = 1,
        heartbeat_seconds: float = 20.0,
        executor: WorkModeToolExecutor | None = None,
    ):
        self.service = service
        self.action_client = action_client
        self.max_turns = max(max_turns, 1)
        self.max_invalid_turns = max(max_invalid_turns, 0)
        self.max_retryable_turn_retries = max(max_retryable_turn_retries, 0)
        self.heartbeat_seconds = max(heartbeat_seconds, 0.0)
        self.executor = executor or WorkModeToolExecutor(service)

    def run(self, user_id: str, mission_id: str, run_id: str) -> dict[str, Any]:
        last_observation: dict[str, Any] | None = None
        invalid_turns = 0
        for turn_index in range(self.max_turns):
            if self.service.should_stop(user_id, mission_id):
                self.service.mark_mission_stopped(user_id, mission_id, run_id, step_id=None)
                return self.service.get_mission_detail(user_id, mission_id)

            context = self._build_context(user_id, mission_id, last_observation, turn_index)
            self._append_model_turn_event(
                user_id,
                mission_id,
                run_id,
                "MODEL_TURN_STARTED",
                "Thinking",
                "Selecting next tool.",
                {"turn": turn_index + 1, "maxTurns": self.max_turns},
            )
            retry_attempt = 0
            try:
                action = self._generate_action_with_retry(
                    user_id,
                    mission_id,
                    run_id,
                    context,
                    turn_index,
                    retry_attempt,
                )
            except ToolActionClientError as exc:
                if exc.retryable:
                    self.service.mark_mission_paused_retryable(
                        user_id,
                        mission_id,
                        run_id,
                        exc.code,
                        metadata={
                            "turn": turn_index + 1,
                            "retryAttempts": self.max_retryable_turn_retries,
                            "retryBudgetExhausted": True,
                        },
                    )
                    return self.service.get_mission_detail(user_id, mission_id)
                invalid_turns += 1
                self._append_model_turn_event(
                    user_id,
                    mission_id,
                    run_id,
                    "MODEL_TURN_INVALID",
                    "Invalid turn",
                    exc.code,
                    {"turn": turn_index + 1, "code": exc.code, "attempt": invalid_turns},
                )
                if invalid_turns > self.max_invalid_turns:
                    self.service.mark_mission_failed(user_id, mission_id, run_id, exc.code, step_id=None)
                    return self.service.get_mission_detail(user_id, mission_id)
                last_observation = {
                    "tool": "validate_tool_call",
                    "status": "invalid",
                    "code": exc.code,
                    "message": str(exc),
                    "instruction": "Return exactly one valid JSON Action using the available tools.",
                }
                continue
            self._append_model_turn_event(
                user_id,
                mission_id,
                run_id,
                "MODEL_TURN_COMPLETED",
                "Tool selected",
                action.tool,
                {"turn": turn_index + 1, "tool": action.tool},
            )
            self._append_model_turn_event(
                user_id,
                mission_id,
                run_id,
                "TOOL_CALLED",
                _tool_title(action.tool),
                _tool_message(action),
                {"turn": turn_index + 1, "tool": action.tool, "arguments": _tool_event_arguments(action)},
            )
            try:
                result = self.executor.execute(user_id, mission_id, run_id, action)
            except HTTPException as exc:
                invalid_turns += 1
                code = str(exc.detail or f"http_{exc.status_code}")
                self._append_model_turn_event(
                    user_id,
                    mission_id,
                    run_id,
                    "MODEL_TURN_INVALID",
                    "Tool rejected",
                    code,
                    {
                        "turn": turn_index + 1,
                        "tool": action.tool,
                        "code": code,
                        "statusCode": exc.status_code,
                        "attempt": invalid_turns,
                        "phase": "tool_execution",
                    },
                )
                if invalid_turns > self.max_invalid_turns:
                    self.service.mark_mission_failed(user_id, mission_id, run_id, code, step_id=None)
                    return self.service.get_mission_detail(user_id, mission_id)
                last_observation = {
                    "tool": action.tool,
                    "status": "rejected",
                    "code": code,
                    "message": code,
                    "statusCode": exc.status_code,
                    "instruction": _tool_rejection_instruction(action.tool, code),
                }
                continue
            except ToolActionClientError as exc:
                if exc.retryable:
                    self.service.mark_mission_paused_retryable(
                        user_id,
                        mission_id,
                        run_id,
                        exc.code,
                        metadata={"turn": turn_index + 1, "tool": action.tool, "phase": "tool_execution"},
                    )
                    return self.service.get_mission_detail(user_id, mission_id)
                self.service.mark_mission_failed(user_id, mission_id, run_id, exc.code, step_id=None)
                return self.service.get_mission_detail(user_id, mission_id)
            invalid_turns = 0
            last_observation = result.observation
            self._publish_test_visible_result(result)
            if result.terminal:
                return self.service.get_mission_detail(user_id, mission_id)

        self.service.mark_mission_failed(
            user_id,
            mission_id,
            run_id,
            error="mission_loop_turn_budget_exceeded",
            step_id=None,
        )
        return self.service.get_mission_detail(user_id, mission_id)

    def _generate_action_with_retry(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        context: dict[str, Any],
        turn_index: int,
        retry_attempt: int,
    ) -> ToolAction:
        try:
            return self._call_action_client_with_heartbeat(user_id, mission_id, run_id, context, turn_index)
        except ToolActionClientError as exc:
            if not exc.retryable or retry_attempt >= self.max_retryable_turn_retries:
                raise
            next_attempt = retry_attempt + 1
            self._append_model_turn_event(
                user_id,
                mission_id,
                run_id,
                "MODEL_TURN_RETRYING",
                "Retrying",
                exc.code,
                {
                    "turn": turn_index + 1,
                    "error": exc.code,
                    "attempt": next_attempt,
                    "maxAttempts": self.max_retryable_turn_retries,
                },
            )
            retry_context = {
                **context,
                "lastObservation": {
                    "tool": "model_turn",
                    "status": "retrying",
                    "code": exc.code,
                    "instruction": "Retry the same decision. Return exactly one valid JSON Action.",
                },
            }
            return self._generate_action_with_retry(
                user_id,
                mission_id,
                run_id,
                retry_context,
                turn_index,
                next_attempt,
            )

    def _call_action_client_with_heartbeat(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        context: dict[str, Any],
        turn_index: int,
    ) -> ToolAction:
        if self.heartbeat_seconds <= 0:
            return self.action_client.generate_action(context)

        started_at = monotonic()
        next_heartbeat_at = started_at + self.heartbeat_seconds
        heartbeat_count = 0
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self.action_client.generate_action, context)
            while not future.done():
                now = monotonic()
                if now >= next_heartbeat_at:
                    heartbeat_count += 1
                    self._append_model_turn_event(
                        user_id,
                        mission_id,
                        run_id,
                        "MODEL_TURN_HEARTBEAT",
                        "Working",
                        "Still selecting next tool.",
                        {
                            "turn": turn_index + 1,
                            "heartbeat": heartbeat_count,
                            "elapsedSeconds": int(now - started_at),
                        },
                    )
                    next_heartbeat_at = now + self.heartbeat_seconds
                sleep(min(0.25, max(self.heartbeat_seconds / 4, 0.01)))
            return future.result()

    def _build_context(
        self,
        user_id: str,
        mission_id: str,
        last_observation: dict[str, Any] | None,
        turn_index: int,
    ) -> dict[str, Any]:
        detail = self.service.get_mission_detail(user_id, mission_id)
        mission = detail["mission"]
        return build_lead_context(
            mission=mission,
            lead_agent=_lead_agent(mission),
            delegate_agent=_delegate_agent(mission),
            products=detail["products"],
            work_windows=detail["workWindows"],
            events=detail["events"],
            artifacts=detail["artifacts"],
            last_observation=last_observation,
            budget={"turn": turn_index + 1, "maxTurns": self.max_turns},
        )

    def _publish_test_visible_result(self, result: ToolExecutionResult) -> None:
        # Keeps fake scripted clients decoupled from repository internals in service-level tests.
        if result.product_id and hasattr(self.action_client, "last_product_id"):
            setattr(self.action_client, "last_product_id", result.product_id)
        if result.artifact_id and hasattr(self.action_client, "last_artifact_id"):
            setattr(self.action_client, "last_artifact_id", result.artifact_id)

    def _append_model_turn_event(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        event_type: str,
        title: str,
        message: str,
        payload: dict[str, Any],
    ) -> None:
        mission = self.service._require_mission(user_id, mission_id)
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type=event_type,
            title=title,
            message=message,
            payload={**payload, "employee": _lead_agent(self.service.get_mission_detail(user_id, mission_id)["mission"])},
        )


def _lead_agent(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission["leadEmployeeId"],
        "name": mission["leadEmployeeName"],
        "role": mission["leadEmployeeRole"],
    }


def _delegate_agent(mission: dict[str, Any]) -> dict[str, str]:
    lead_id = mission["leadEmployeeId"]
    if lead_id == "agent_1":
        return {"id": "agent_2", "name": "Agent 2", "role": "Delegate Agent"}
    if lead_id == "agent_2":
        return {"id": "agent_1", "name": "Agent 1", "role": "Delegate Agent"}
    return {"id": "agent_2", "name": "Agent 2", "role": "Delegate Agent"}


def _tool_title(tool: str) -> str:
    return {
        "mission_plan": "Plan",
        "work_product": "Product",
        "inspect_product": "Inspect",
        "delegate_agent": "Delegate",
        "ask_user": "Ask",
        "finish_mission": "Finish",
        "block_mission": "Block",
        "review_product": "Review",
        "discuss_with_delegate": "Discuss",
        "evaluate_product": "Evaluate",
        "web_search": "Search",
    }.get(tool, "Tool")


def _tool_message(action: ToolAction) -> str:
    reason = getattr(action.arguments, "reason", "")
    return reason or action.tool


def _tool_event_arguments(action: ToolAction) -> dict[str, Any]:
    values = action.arguments.model_dump(by_alias=True)
    if "content" in values:
        values["contentPreview"] = str(values.pop("content"))[:320]
    if "brief" in values:
        values["briefPreview"] = str(values.pop("brief"))[:320]
    return values


def _tool_rejection_instruction(tool: str, code: str) -> str:
    if tool == "finish_mission" and code in {
        "final_artifact_required",
        "final_artifact_not_in_final_product",
        "final_artifact_not_final_content",
        "final_artifact_cjk_too_short",
        "missing_outline_artifact",
        "missing_chapter_artifact",
        "final_paper_draft_required",
        "reliability_evaluation_required",
        "reliability_evaluation_needs_review",
    }:
        if code in {"reliability_evaluation_required", "reliability_evaluation_needs_review"}:
            return (
                "Repair quality before finishing: call evaluate_product after the final candidate, then use "
                "web_search, discuss_with_delegate, or work_product to resolve blocking Reliability issues before "
                "calling finish_mission again."
            )
        return (
            "Repair the Product before finishing: call work_product on the existing Product, create or revise an "
            'Artifact with artifactKind="final", include the complete final deliverable content, then call '
            "finish_mission with that final Artifact id."
        )
    if code in {"product_not_found", "artifact_not_found"}:
        return (
            "Use only Product and Artifact ids from productManifest, recentArtifactContent, or inspect_product. "
            "Call inspect_product if you need to confirm the correct references."
        )
    return "Choose the next valid tool call that repairs this rejected tool request."
