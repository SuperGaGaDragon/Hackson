"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

EvaluationProfile = Literal["research_reliability_v1"]
ReliabilityStatus = Literal["ship_ready", "minor_review", "needs_human_review", "unsafe_to_ship"]
IssueSeverity = Literal["critical", "high", "medium", "low"]
IssueType = Literal[
    "missing_requirement",
    "partial_requirement",
    "unsupported_claim",
    "weakly_supported_claim",
    "contradicted_claim",
    "hallucinated_entity",
    "missing_source",
    "tool_failure_ignored",
    "unsafe_action",
    "evaluation_limitation",
    "mission_incomplete",
]
RequirementType = Literal["count", "field", "constraint", "format", "action", "safety"]
RequirementStatus = Literal["met", "partially_met", "missing", "not_evaluable"]
ClaimType = Literal["existence", "location", "product", "customer", "funding", "founding", "other"]
SupportLevel = Literal["strong", "weak", "none", "contradicted", "not_evaluable"]


class RequirementItem(BaseModel):
    id: str
    requirement: str
    type: RequirementType
    priority: Literal["must", "should"] = "must"
    status: RequirementStatus
    evidence: str = ""
    expected_count: int | None = Field(default=None, alias="expectedCount")
    field_name: str | None = Field(default=None, alias="fieldName")

    model_config = ConfigDict(populate_by_name=True)


class ClaimItem(BaseModel):
    id: str
    text: str
    entity: str = ""
    claim_type: ClaimType = Field(default="other", alias="claimType")
    needs_evidence: bool = Field(default=True, alias="needsEvidence")
    artifact_id: str = Field(alias="artifactId")
    support_level: SupportLevel = Field(default="not_evaluable", alias="supportLevel")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    best_evidence_ids: list[str] = Field(default_factory=list, alias="bestEvidenceIds")
    reason: str = ""

    model_config = ConfigDict(populate_by_name=True)


class EvidenceItem(BaseModel):
    id: str
    title: str
    url: str
    source: str = ""
    snippet: str = ""
    event_id: str = Field(alias="eventId")
    event_sequence: int = Field(alias="eventSequence")
    provider: str = ""
    published_at: str | None = Field(default=None, alias="publishedAt")

    model_config = ConfigDict(populate_by_name=True)


class ReliabilityIssue(BaseModel):
    id: str
    type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    claim_ids: list[str] = Field(default_factory=list, alias="claimIds")
    requirement_ids: list[str] = Field(default_factory=list, alias="requirementIds")
    evidence_ids: list[str] = Field(default_factory=list, alias="evidenceIds")
    event_ids: list[str] = Field(default_factory=list, alias="eventIds")
    artifact_ids: list[str] = Field(default_factory=list, alias="artifactIds")
    suggested_fix: str = Field(default="", alias="suggestedFix")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def require_fix_for_serious_issues(self) -> "ReliabilityIssue":
        if self.severity in {"critical", "high"} and not self.suggested_fix.strip():
            raise ValueError("serious_issue_requires_suggested_fix")
        return self


class ReliabilityReport(BaseModel):
    report_id: str = Field(alias="reportId")
    mission_id: str = Field(alias="missionId")
    profile: EvaluationProfile
    score: int = Field(ge=0, le=100)
    status: ReliabilityStatus
    summary: str
    requirements: list[RequirementItem] = Field(default_factory=list)
    claims: list[ClaimItem] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    issues: list[ReliabilityIssue] = Field(default_factory=list)
    issue_counts: dict[str, int] = Field(default_factory=dict, alias="issueCounts")
    suggested_next_actions: list[str] = Field(default_factory=list, alias="suggestedNextActions")
    limitations: list[str] = Field(default_factory=list)
    report_artifact_id: str | None = Field(default=None, alias="reportArtifactId")

    model_config = ConfigDict(populate_by_name=True)
