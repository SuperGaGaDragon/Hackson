"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

import json
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ToolName = Literal[
    "mission_plan",
    "work_product",
    "inspect_product",
    "delegate_agent",
    "ask_user",
    "finish_mission",
    "block_mission",
    "review_product",
    "discuss_with_delegate",
    "web_search",
    "evaluate_product",
]


class ToolActionValidationError(ValueError):
    """Stable parser/validator error for invalid model tool turns."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class MissionPlanStep(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    status: Literal["pending", "in_progress", "completed", "changed"]
    notes: str = Field(default="", max_length=1000)


class MissionPlanArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    plan_title: str = Field(min_length=1, max_length=200, alias="planTitle")
    steps: list[MissionPlanStep] = Field(min_length=1, max_length=20)

    model_config = ConfigDict(populate_by_name=True)


class WorkProductArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    operation: Literal["create_product", "append_artifact", "revise_artifact", "finalize_product"]
    product_id: str | None = Field(default=None, alias="productId")
    source_artifact_ids: list[str] = Field(default_factory=list, alias="sourceArtifactIds")
    product_title: str = Field(min_length=1, max_length=200, alias="productTitle")
    artifact_title: str = Field(min_length=1, max_length=200, alias="artifactTitle")
    artifact_kind: Literal["outline", "chapter", "draft", "revision", "final", "report", "notes", "other"] = Field(
        alias="artifactKind"
    )
    content: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=1000)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_product_reference(self) -> "WorkProductArguments":
        if self.operation == "create_product" and self.product_id is not None:
            raise ValueError("create_product_must_not_reference_existing_product")
        if self.operation != "create_product" and not self.product_id:
            raise ValueError("product_id_required_for_existing_product_operation")
        return self


class InspectProductArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    product_ids: list[str] = Field(default_factory=list, alias="productIds")
    artifact_ids: list[str] = Field(default_factory=list, alias="artifactIds")
    focus: str = Field(default="", max_length=1000)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_inspection_target(self) -> "InspectProductArguments":
        if not self.product_ids and not self.artifact_ids:
            raise ValueError("inspect_product_requires_product_or_artifact")
        return self


class DelegateAgentArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    agent_slot: Literal["agent_1", "agent_2"] = Field(alias="agentSlot")
    window_title: str = Field(min_length=1, max_length=200, alias="windowTitle")
    brief: str = Field(min_length=1, max_length=8000)
    expected_output: Literal["outline", "chapter", "review", "revision", "summary", "other"] = Field(
        alias="expectedOutput"
    )
    target_product_id: str | None = Field(default=None, alias="targetProductId")
    source_artifact_ids: list[str] = Field(default_factory=list, alias="sourceArtifactIds")

    model_config = ConfigDict(populate_by_name=True)


class AskUserArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    question: str = Field(min_length=1, max_length=2000)
    suggested_options: list[str] = Field(default_factory=list, max_length=6, alias="suggestedOptions")

    model_config = ConfigDict(populate_by_name=True)


class FinishMissionArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    summary: str = Field(min_length=1, max_length=2000)
    final_product_ids: list[str] = Field(min_length=1, alias="finalProductIds")
    final_artifact_ids: list[str] = Field(default_factory=list, alias="finalArtifactIds")

    model_config = ConfigDict(populate_by_name=True)


class BlockMissionArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    blocked_reason: str = Field(min_length=1, max_length=2000, alias="blockedReason")
    needed_from_user: str = Field(default="", max_length=2000, alias="neededFromUser")

    model_config = ConfigDict(populate_by_name=True)


class ReviewFinding(BaseModel):
    severity: Literal["critical", "major", "minor"]
    area: Literal["requirement", "structure", "length", "consistency", "style", "readability", "other"]
    claim: str = Field(min_length=1, max_length=1000)
    evidence: str = Field(default="", max_length=2000)
    required_change: str = Field(default="", max_length=2000, alias="requiredChange")

    model_config = ConfigDict(populate_by_name=True)


class ReviewProductArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    product_ids: list[str] = Field(default_factory=list, alias="productIds")
    artifact_ids: list[str] = Field(default_factory=list, alias="artifactIds")
    review_title: str = Field(min_length=1, max_length=200, alias="reviewTitle")
    review_profile: Literal["long_form_novel_v1", "general_text_v1"] = Field(alias="reviewProfile")
    verdict: Literal["pass", "needs_revision", "blocked"]
    score: int = Field(ge=0, le=100)
    summary: str = Field(min_length=1, max_length=2000)
    findings: list[ReviewFinding] = Field(default_factory=list, max_length=20)
    passed_checks: list[str] = Field(default_factory=list, alias="passedChecks")
    recommended_next_tool: Literal[
        "work_product",
        "discuss_with_delegate",
        "finish_mission",
        "ask_user",
        "block_mission",
    ] = Field(alias="recommendedNextTool")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_review_target(self) -> "ReviewProductArguments":
        if not self.product_ids and not self.artifact_ids:
            raise ValueError("review_product_requires_product_or_artifact")
        return self


class DiscussWithDelegateArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    agent_slot: Literal["agent_1", "agent_2"] = Field(alias="agentSlot")
    discussion_title: str = Field(min_length=1, max_length=200, alias="discussionTitle")
    window_id: str | None = Field(default=None, alias="windowId")
    product_id: str | None = Field(default=None, alias="productId")
    artifact_ids: list[str] = Field(default_factory=list, alias="artifactIds")
    question: str = Field(min_length=1, max_length=4000)
    expected_outcome: str = Field(min_length=1, max_length=2000, alias="expectedOutcome")
    max_turns: int = Field(default=1, ge=1, le=3, alias="maxTurns")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_discussion_binding(self) -> "DiscussWithDelegateArguments":
        if not self.window_id and not self.product_id and not self.artifact_ids:
            raise ValueError("discussion_requires_product_artifact_or_window")
        return self


class WebSearchArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    query: str = Field(min_length=1, max_length=500)
    search_type: Literal["general", "news", "technical", "reference"] = Field(default="general", alias="searchType")
    max_results: int = Field(default=5, ge=1, le=10, alias="maxResults")
    recency_days: int | None = Field(default=None, ge=0, le=3650, alias="recencyDays")
    allowed_domains: list[str] = Field(default_factory=list, max_length=10, alias="allowedDomains")
    blocked_domains: list[str] = Field(default_factory=list, max_length=10, alias="blockedDomains")

    model_config = ConfigDict(populate_by_name=True)


class EvaluateProductArguments(BaseModel):
    reason: str = Field(min_length=1, max_length=240)
    profile: Literal["research_reliability_v1"] = "research_reliability_v1"
    product_ids: list[str] = Field(default_factory=list, alias="productIds")
    artifact_ids: list[str] = Field(default_factory=list, alias="artifactIds")
    focus: str = Field(default="", max_length=1000)

    model_config = ConfigDict(populate_by_name=True)


ToolArguments = (
    MissionPlanArguments
    | WorkProductArguments
    | InspectProductArguments
    | DelegateAgentArguments
    | AskUserArguments
    | FinishMissionArguments
    | BlockMissionArguments
    | ReviewProductArguments
    | DiscussWithDelegateArguments
    | WebSearchArguments
    | EvaluateProductArguments
)


class ToolAction(BaseModel):
    tool: ToolName
    arguments: ToolArguments


class RawToolAction(BaseModel):
    tool: ToolName
    arguments: dict


def parse_tool_action(raw_text: str) -> ToolAction:
    """Parse and validate one model-produced Work Mode tool action."""
    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ToolActionValidationError("tool_action_invalid_json", "model_turn_must_be_json") from exc

    if isinstance(raw, list):
        raise ToolActionValidationError("tool_action_multiple_calls", "model_turn_must_contain_one_tool_call")
    if not isinstance(raw, dict):
        raise ToolActionValidationError("tool_action_invalid_shape", "model_turn_must_be_json_object")

    try:
        action = RawToolAction.model_validate(raw)
    except ValidationError as exc:
        if _has_literal_error(exc, "tool"):
            raise ToolActionValidationError("tool_action_unknown_tool", "tool_is_not_allowed") from exc
        raise ToolActionValidationError("tool_action_schema_invalid", "tool_action_schema_invalid") from exc

    arguments = _validate_arguments(action.tool, action.arguments)
    return ToolAction(tool=action.tool, arguments=arguments)


def _validate_arguments(tool: ToolName, raw_arguments: dict) -> ToolArguments:
    model = _argument_model(tool)
    try:
        return model.model_validate(raw_arguments)
    except ValidationError as exc:
        raise ToolActionValidationError("tool_action_schema_invalid", "tool_action_schema_invalid") from exc


def _argument_model(tool: ToolName) -> type[ToolArguments]:
    return {
        "mission_plan": MissionPlanArguments,
        "work_product": WorkProductArguments,
        "inspect_product": InspectProductArguments,
        "delegate_agent": DelegateAgentArguments,
        "ask_user": AskUserArguments,
        "finish_mission": FinishMissionArguments,
        "block_mission": BlockMissionArguments,
        "review_product": ReviewProductArguments,
        "discuss_with_delegate": DiscussWithDelegateArguments,
        "web_search": WebSearchArguments,
        "evaluate_product": EvaluateProductArguments,
    }[tool]


def _has_literal_error(error: ValidationError, field_name: str) -> bool:
    for item in error.errors():
        location = item.get("loc", ())
        if location == (field_name,) and item.get("type") == "literal_error":
            return True
    return False
