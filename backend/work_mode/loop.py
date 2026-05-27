"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from typing import Any, Protocol

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
        executor: WorkModeToolExecutor | None = None,
    ):
        self.service = service
        self.action_client = action_client
        self.max_turns = max(max_turns, 1)
        self.max_invalid_turns = max(max_invalid_turns, 0)
        self.executor = executor or WorkModeToolExecutor(service)

    def run(self, user_id: str, mission_id: str, run_id: str) -> dict[str, Any]:
        last_observation: dict[str, Any] | None = None
        invalid_turns = 0
        for turn_index in range(self.max_turns):
            if self.service.should_stop(user_id, mission_id):
                self.service.mark_mission_stopped(user_id, mission_id, run_id, step_id=None)
                return self.service.get_mission_detail(user_id, mission_id)

            context = self._build_context(user_id, mission_id, last_observation, turn_index)
            try:
                action = self.action_client.generate_action(context)
            except ToolActionClientError as exc:
                if exc.retryable:
                    self.service.mark_mission_paused_retryable(user_id, mission_id, run_id, exc.code)
                    return self.service.get_mission_detail(user_id, mission_id)
                invalid_turns += 1
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
            invalid_turns = 0
            result = self.executor.execute(user_id, mission_id, run_id, action)
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
