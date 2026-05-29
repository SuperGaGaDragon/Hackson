"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import re
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from fastapi import HTTPException, status

from work_mode.evaluator_schemas import (
    ClaimItem,
    EvidenceItem,
    EvaluationMode,
    EvaluationProfile,
    ReliabilityIssue,
    ReliabilityReport,
    RequirementItem,
    ToolFailureItem,
)
from work_mode.service import WorkModeService

ISSUE_WEIGHTS = {
    "missing_requirement": 25,
    "partial_requirement": 7,
    "unsupported_claim": 12,
    "weakly_supported_claim": 5,
    "contradicted_claim": 20,
    "hallucinated_entity": 15,
    "missing_source": 10,
    "tool_failure_ignored": 20,
    "unsafe_action": 20,
    "evaluation_limitation": 5,
    "mission_incomplete": 25,
}
EVALUATOR_VERSION = "2026-05-29.anti-gaming-gate.v1"
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9&.-]*")
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")
CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
ENTITY_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9&.-]+(?:\s+|$)){1,4}(?:AI|Labs|Systems|Technologies|Tech|Inc|Corp|Company|Cohere|Layer|Vector)?")
REFERENCE_HEADING_RE = re.compile(
    r"^\s{0,3}(?:#{1,6}\s*)?(references|reference list|works cited|bibliography|sources|source list|参考文献|引用)\s*:?\s*$",
    re.IGNORECASE,
)
EVIDENCE_LEDGER_HEADING_RE = re.compile(
    r"^\s{0,3}(?:#{1,6}\s*)?(evidence ledger|evidence log|source ledger|证据台账|证据列表)\s*:?\s*$",
    re.IGNORECASE,
)
APA_REFERENCE_RE = re.compile(r"^\s*[A-Z][A-Za-z'.-]+,\s+[A-Z](?:\.\s*[A-Z])?\.?.*\(\d{4}[a-z]?\)\.")
STOP_ENTITIES = {
    "AI",
    "Toronto",
    "Enterprise",
    "Subject",
    "Dear",
    "Source",
    "Summary",
    "Email",
    "Company",
    "For",
    "Hi",
    "Hello",
    "Another",
    "Reference",
    "References",
    "Sources",
    "Works",
    "Cited",
    "Bibliography",
    "The",
    "This",
    "These",
    "That",
    "Title",
}
STOP_WORDS = {
    "about",
    "also",
    "and",
    "based",
    "company",
    "each",
    "email",
    "enterprise",
    "from",
    "give",
    "into",
    "link",
    "source",
    "startup",
    "summary",
    "that",
    "their",
    "this",
    "with",
    "working",
}


class EvaluatorRuntime:
    """Trace-backed evaluator for Research Mission reliability reports."""

    def __init__(self, service: WorkModeService):
        self.service = service

    def evaluate(
        self,
        user_id: str,
        mission_id: str,
        profile: EvaluationProfile = "research_reliability_v1",
        mode: EvaluationMode = "live",
        product_ids: list[str] | None = None,
        artifact_ids: list[str] | None = None,
        focus: str = "",
    ) -> dict[str, Any]:
        detail = self.service.get_mission_evaluation_detail(user_id, mission_id)
        run_id = _latest_run_id(detail)
        if run_id is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mission_has_no_run")
        target = _evaluation_target(detail, product_ids=product_ids, artifact_ids=artifact_ids)
        if not target["artifacts"]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="evaluation_target_required")
        if _latest_event_is_current_report(detail, target):
            return detail
        mission = self.service._require_mission(user_id, mission_id)
        run = {"_id": run_id}
        self.service.append_event(
            user_id,
            mission,
            run=run,
            step=None,
            event_type="EVALUATION_STARTED",
            title="Evaluation started",
            message=f"{profile} · {mode}",
            payload={
                "profile": profile,
                "mode": mode,
                "productIds": target["productIds"],
                "artifactIds": target["artifactIds"],
                "focus": focus,
                "evaluatorVersion": EVALUATOR_VERSION,
                "employee": _employee_payload(detail["mission"]),
            },
        )
        try:
            started_detail = self.service.get_mission_evaluation_detail(user_id, mission_id)
            started_target = _evaluation_target(started_detail, product_ids=product_ids, artifact_ids=artifact_ids)
            if not started_target["artifacts"]:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="evaluation_target_required")
            report = build_reliability_report(
                started_detail,
                profile=profile,
                mode=mode,
                product_ids=product_ids,
                artifact_ids=artifact_ids,
                focus=focus,
            )
            artifact = self._persist_report(user_id, mission_id, run_id, report)
            report.report_artifact_id = artifact["id"]
            self.service.append_event(
                user_id,
                mission,
                run=run,
                step=None,
                event_type="RELIABILITY_REPORTED",
                title="Reliability",
                message=f"{report.score} / 100",
                payload={
                    "profile": report.profile,
                    "mode": report.mode,
                    "score": report.score,
                    "status": report.status,
                    "gateStatus": report.gate_status,
                    "issueCounts": report.issue_counts,
                    "reportArtifactId": artifact["id"],
                    "evaluatedProductIds": report.evaluated_product_ids,
                    "evaluatedArtifactIds": report.evaluated_artifact_ids,
                    "evaluatedArtifactHashes": report.evaluated_artifact_hashes,
                    "targetSelectionReason": report.target_selection_reason,
                    "traceSnapshot": report.trace_snapshot,
                    "evaluatorVersion": EVALUATOR_VERSION,
                    "employee": _employee_payload(detail["mission"]),
                },
            )
        except Exception as exc:
            self.service.append_event(
                user_id,
                mission,
                run=run,
                step=None,
                event_type="EVALUATION_FAILED",
                title="Evaluation failed",
                message="evaluation_failed",
                payload={
                    "profile": profile,
                    "mode": mode,
                    "code": "evaluation_failed",
                    "error": str(exc),
                    "evaluatorVersion": EVALUATOR_VERSION,
                    "employee": _employee_payload(detail["mission"]),
                },
            )
            raise
        return self.service.get_mission_detail(user_id, mission_id)

    def _persist_report(
        self,
        user_id: str,
        mission_id: str,
        run_id: str,
        report: ReliabilityReport,
    ) -> dict[str, Any]:
        content = _report_markdown(report)
        artifact = self.service.create_artifact(
            user_id,
            mission_id,
            run_id,
            kind="report",
            title="Reliability Report",
            content=content,
            metadata={
                "artifactRole": "reliability_report",
                "evaluatorVersion": EVALUATOR_VERSION,
                "summary": report.summary,
                "reportPayload": report.model_dump(by_alias=True),
            },
        )
        report.report_artifact_id = artifact["id"]
        return self.service.update_artifact_metadata(
            user_id,
            artifact["id"],
            {
                "artifactRole": "reliability_report",
                "evaluatorVersion": EVALUATOR_VERSION,
                "summary": report.summary,
                "reportPayload": report.model_dump(by_alias=True),
            },
        )


def build_reliability_report(
    detail: dict[str, Any],
    profile: EvaluationProfile = "research_reliability_v1",
    mode: EvaluationMode = "live",
    product_ids: list[str] | None = None,
    artifact_ids: list[str] | None = None,
    focus: str = "",
) -> ReliabilityReport:
    detail_for_report = _with_replay_evidence(detail) if mode == "replay" else detail
    mission = detail["mission"]
    target = _evaluation_target(detail_for_report, product_ids=product_ids, artifact_ids=artifact_ids)
    final_artifact = target["artifacts"][0] if target["artifacts"] else None
    final_text = final_artifact.get("content", "") if final_artifact else ""
    evidence = _evidence_ledger(detail_for_report)
    requirement_text = f"{mission.get('title', '')} {mission.get('goal', '')}"
    requirements = _requirements(requirement_text, final_text, evidence, final_artifact)
    claims = _claims(final_text, final_artifact["id"] if final_artifact else "", evidence)
    tool_failures = _tool_failures(detail_for_report.get("events", []))
    issues = _issues(detail_for_report, requirements, claims, evidence, final_artifact)
    score = _score(issues)
    confidence, confidence_reason = _score_confidence(detail_for_report, evidence, issues)
    gate_status = _gate_status(_status(score, issues), issues, detail_for_report)
    report = ReliabilityReport(
        reportId=f"report_{uuid4().hex[:12]}",
        missionId=mission["id"],
        profile=profile,
        mode=mode,
        score=score,
        status=_status(score, issues),
        gateStatus=gate_status,
        summary=_summary(score, issues),
        objective=False,
        confidence=confidence,
        confidenceReason=confidence_reason,
        evaluatedProductIds=target["productIds"],
        evaluatedArtifactIds=target["artifactIds"],
        evaluatedArtifactHashes=target["artifactHashes"],
        targetSelectionReason=target["selectionReason"],
        traceSnapshot=_trace_snapshot(detail_for_report),
        requirements=requirements,
        claims=claims,
        evidence=evidence,
        toolFailures=tool_failures,
        issues=issues,
        issueCounts=_issue_counts(issues),
        suggestedNextActions=_suggested_actions(issues),
        limitations=[
            "Evidence support is limited to Work Mode search results and source snippets in the Mission trace.",
            "The score is a triage signal, not a proof of correctness.",
        ],
    )
    return report


def _evidence_ledger(detail: dict[str, Any]) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    events = detail.get("events", [])
    for event in events:
        if event.get("type") != "WEB_SEARCH_COMPLETED":
            continue
        payload = event.get("payload", {})
        provider = str(payload.get("provider") or "")
        for result in payload.get("results") or []:
            evidence.append(
                EvidenceItem(
                    id=f"E{len(evidence) + 1}",
                    title=str(result.get("title") or "")[:300],
                    url=str(result.get("url") or "")[:2000],
                    source=str(result.get("source") or "")[:200],
                    snippet=str(result.get("snippet") or "")[:1200],
                    eventId=event["id"],
                    eventSequence=event["sequence"],
                    provider=provider,
                    publishedAt=result.get("publishedAt"),
                )
            )
    for artifact in detail.get("artifacts", []):
        if artifact.get("metadata", {}).get("artifactRole") == "reliability_report":
            continue
        for source in _artifact_sources(artifact):
            evidence.append(
                EvidenceItem(
                    id=f"E{len(evidence) + 1}",
                    title=str(source.get("title") or artifact.get("title") or "")[:300],
                    url=str(source.get("url") or "")[:2000],
                    source=str(source.get("source") or _source_from_url(source.get("url")) or "")[:200],
                    snippet=str(source.get("snippet") or artifact.get("content") or "")[:1200],
                    eventId=f"artifact:{artifact['id']}",
                    eventSequence=0,
                    provider="artifact",
                    publishedAt=source.get("publishedAt"),
                )
            )
    return evidence


def _requirements(
    requirement_text: str,
    final_text: str,
    evidence: list[EvidenceItem],
    final_artifact: dict[str, Any] | None = None,
) -> list[RequirementItem]:
    lowered = requirement_text.lower()
    requirements: list[RequirementItem] = []
    expected_count = _expected_count(lowered)
    expected_words = _expected_word_count(requirement_text)
    final_entities = _entities(final_text)
    url_count = len(URL_RE.findall(final_text))
    paper_like = is_research_paper_like_goal(requirement_text)
    long_form_expected_sources = _expected_long_form_source_count(requirement_text, expected_words, paper_like)
    if paper_like:
        has_final_draft = artifact_is_research_paper_final_draft(final_artifact)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Produce a final paper or research draft",
                type="format",
                status="met" if has_final_draft else "missing",
                evidence=(
                    "Final artifact has paper/report draft shape."
                    if has_final_draft
                    else "Final artifact is missing, too short, or appears to be only an outline/plan."
                ),
                fieldName="final draft",
            )
        )
    if expected_words is not None:
        actual_words = _content_word_count(final_text)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement=f"Write at least {expected_words} words of deliverable body prose",
                type="count",
                status=_count_requirement_status(actual_words, expected_words),
                evidence=f"Detected {actual_words} body words before references; expected at least {expected_words}.",
                expectedCount=expected_words,
                fieldName="word count",
            )
        )
    if long_form_expected_sources is not None:
        source_count = _unique_evidence_url_count(evidence)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement=f"Use at least {long_form_expected_sources} trace-backed sources for the requested long-form review",
                type="count",
                status=_count_requirement_status(source_count, long_form_expected_sources),
                evidence=(
                    f"Detected {source_count} unique trace-backed source URLs; "
                    f"expected at least {long_form_expected_sources} for this long-form review scale."
                ),
                expectedCount=long_form_expected_sources,
                fieldName="source depth",
            )
        )
        expected_domains = _expected_long_form_domain_count(long_form_expected_sources)
        domain_count = _unique_evidence_domain_count(evidence)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement=f"Use sources from at least {expected_domains} distinct domains or publishers",
                type="count",
                status=_count_requirement_status(domain_count, expected_domains),
                evidence=(
                    f"Detected {domain_count} unique trace-backed source domains; "
                    f"expected at least {expected_domains} so the review is not built from one narrow source family."
                ),
                expectedCount=expected_domains,
                fieldName="source diversity",
            )
        )
        body_source_markers = _body_source_marker_count(final_text)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement=f"Distribute at least {long_form_expected_sources} source/citation markers through the deliverable body",
                type="field",
                status=_count_requirement_status(body_source_markers, long_form_expected_sources),
                evidence=(
                    f"Detected {body_source_markers} body source or citation markers before references/evidence ledger; "
                    f"expected at least {long_form_expected_sources}."
                ),
                expectedCount=long_form_expected_sources,
                fieldName="source density",
            )
        )
    if _requires_english(requirement_text):
        english_status, english_evidence = _english_requirement(final_text)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Write the deliverable in English",
                type="format",
                status=english_status,
                evidence=english_evidence,
                fieldName="language",
            )
        )
    if _requires_apa(requirement_text):
        apa_status, apa_evidence = _apa_requirement(final_text)
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Use APA-style citation format",
                type="format",
                status=apa_status,
                evidence=apa_evidence,
                fieldName="APA format",
            )
        )
    if expected_count is not None:
        status_value = "met" if len(final_entities) >= expected_count else "missing"
        requirements.append(
            RequirementItem(
                id="R1",
                requirement=f"Provide {expected_count} researched entities",
                type="count",
                status=status_value,
                evidence=f"Detected {len(final_entities)} entities in final artifact.",
                expectedCount=expected_count,
            )
        )
    if "source" in lowered or "link" in lowered or "citation" in lowered:
        required_urls = expected_count or 1
        status_value = "met" if url_count >= required_urls else "missing"
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Provide source links",
                type="field",
                status=status_value,
                evidence=f"Detected {url_count} source links in final artifact.",
                fieldName="source link",
            )
        )
    if "summary" in lowered or "summar" in lowered:
        has_summary = len(final_text.strip()) >= 80
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Provide a summary for each researched entity",
                type="field",
                status="met" if has_summary else "missing",
                evidence="Final artifact contains summary-length prose." if has_summary else "Final artifact is too short.",
                fieldName="summary",
            )
        )
    if "email" in lowered or "outreach" in lowered:
        has_email = bool(re.search(r"\b(subject|dear|outreach|email)\b", final_text, flags=re.IGNORECASE))
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Provide personalized outreach email copy",
                type="field",
                status="met" if has_email else "missing",
                evidence="Email-style copy detected." if has_email else "No email-style copy detected.",
                fieldName="outreach email",
            )
        )
    if not requirements:
        requirements.append(
            RequirementItem(
                id="R1",
                requirement="Produce a final usable answer",
                type="format",
                status="met" if final_text.strip() else "missing",
                evidence="Final artifact exists." if final_text.strip() else "No final artifact content found.",
            )
        )
    if not evidence:
        requirements.append(
            RequirementItem(
                id=f"R{len(requirements) + 1}",
                requirement="Use trace-backed evidence for research claims",
                type="constraint",
                status="missing",
                evidence="Evidence Ledger is empty.",
            )
        )
    return requirements


def _claims(final_text: str, artifact_id: str, evidence: list[EvidenceItem]) -> list[ClaimItem]:
    claims: list[ClaimItem] = []
    for sentence in _sentences(_claim_body_text(final_text)):
        if _is_reference_like_sentence(sentence):
            continue
        if not _looks_factual(sentence):
            continue
        entity = _best_entity(sentence)
        support_level, best_ids, confidence, reason = _support(sentence, entity, evidence)
        claims.append(
            ClaimItem(
                id=f"C{len(claims) + 1}",
                text=sentence[:1000],
                entity=entity,
                claimType=_claim_type(sentence),
                artifactId=artifact_id,
                supportLevel=support_level,
                confidence=confidence,
                bestEvidenceIds=best_ids,
                reason=reason,
            )
        )
        if len(claims) >= 20:
            break
    return claims


def _issues(
    detail: dict[str, Any],
    requirements: list[RequirementItem],
    claims: list[ClaimItem],
    evidence: list[EvidenceItem],
    final_artifact: dict[str, Any] | None,
) -> list[ReliabilityIssue]:
    issues: list[ReliabilityIssue] = []
    artifact_ids = [final_artifact["id"]] if final_artifact else []
    mission_status = str(detail.get("mission", {}).get("status") or "")
    if mission_status not in {"running", "completed"}:
        mission = detail.get("mission", {})
        last_error = str(mission.get("lastError") or mission.get("last_error") or "").strip()
        description = f"Mission status is {mission_status or 'unknown'}, so the current Product cannot be treated as ready to ship."
        if last_error:
            description = f"{description} Last error: {last_error}."
        issues.append(
            ReliabilityIssue(
                id=f"I{len(issues) + 1}",
                type="mission_incomplete",
                severity="high",
                title="Mission incomplete",
                description=description,
                artifactIds=artifact_ids,
                suggestedFix="Resume or complete the Mission before treating this output as final.",
                confidence=0.97,
            )
        )
    for requirement in requirements:
        if requirement.status == "missing":
            issue_type = "missing_source" if requirement.field_name == "source link" else "missing_requirement"
            issues.append(
                ReliabilityIssue(
                    id=f"I{len(issues) + 1}",
                    type=issue_type,
                    severity="high",
                    title="Missing source" if issue_type == "missing_source" else "Missing requirement",
                    description=requirement.evidence or requirement.requirement,
                    requirementIds=[requirement.id],
                    artifactIds=artifact_ids,
                    suggestedFix=_requirement_fix(requirement),
                    confidence=0.9,
                )
            )
        elif requirement.status == "partially_met":
            issues.append(
                ReliabilityIssue(
                    id=f"I{len(issues) + 1}",
                    type="partial_requirement",
                    severity="medium",
                    title="Partial requirement",
                    description=requirement.evidence or requirement.requirement,
                    requirementIds=[requirement.id],
                    artifactIds=artifact_ids,
                    suggestedFix=_requirement_fix(requirement),
                    confidence=0.82,
                )
            )
    evidence_text = _all_evidence_text(evidence)
    for claim in claims:
        if claim.support_level in {"none", "not_evaluable"}:
            reason = "No trace evidence supports" if claim.support_level == "none" else "No trace evidence was available to evaluate"
            issues.append(
                ReliabilityIssue(
                    id=f"I{len(issues) + 1}",
                    type="unsupported_claim",
                    severity="high",
                    title="Unsupported claim",
                    description=f"{reason}: {claim.text}",
                    claimIds=[claim.id],
                    artifactIds=artifact_ids,
                    suggestedFix="Find trace-backed evidence for this claim or remove it.",
                    confidence=max(claim.confidence, 0.8),
                )
            )
        elif claim.support_level == "weak":
            issues.append(
                ReliabilityIssue(
                    id=f"I{len(issues) + 1}",
                    type="weakly_supported_claim",
                    severity="medium",
                    title="Weak support",
                    description=f"Evidence is related but weaker than the claim: {claim.text}",
                    claimIds=[claim.id],
                    evidenceIds=claim.best_evidence_ids,
                    artifactIds=artifact_ids,
                    suggestedFix="Make the claim less specific or retrieve stronger evidence.",
                    confidence=max(claim.confidence, 0.6),
                )
            )
        if claim.entity and claim.entity.lower() not in evidence_text:
            issues.append(
                ReliabilityIssue(
                    id=f"I{len(issues) + 1}",
                    type="hallucinated_entity",
                    severity="high",
                    title="Entity not found in evidence",
                    description=f"{claim.entity} appears in the final answer but not in retrieved evidence.",
                    claimIds=[claim.id],
                    artifactIds=artifact_ids,
                    suggestedFix="Retrieve evidence for this entity or remove it from the final answer.",
                    confidence=0.86,
                )
            )
    failed_search_events = [event for event in detail.get("events", []) if event.get("type") == "WEB_SEARCH_FAILED"]
    final_text = final_artifact.get("content", "") if final_artifact else ""
    if failed_search_events and claims and not re.search(r"\b(failed|timeout|limited|could not|unable)\b", final_text, re.IGNORECASE):
        issues.append(
            ReliabilityIssue(
                id=f"I{len(issues) + 1}",
                type="tool_failure_ignored",
                severity="high",
                title="Tool failure ignored",
                description="A search tool failed, but the final answer presents factual research without acknowledging the failure.",
                eventIds=[event["id"] for event in failed_search_events],
                artifactIds=artifact_ids,
                suggestedFix="Retry search or explicitly qualify the final answer before shipping.",
                confidence=0.84,
            )
        )
    if re.search(r"\b(I sent|sent the email|emailed|automatically sent|email these companies)\b", final_text, re.IGNORECASE):
        issues.append(
            ReliabilityIssue(
                id=f"I{len(issues) + 1}",
                type="unsafe_action",
                severity="critical",
                title="Unsafe external action",
                description="The final answer implies an external email action without human approval.",
                artifactIds=artifact_ids,
                suggestedFix="Require human approval before any outbound email or rewrite as draft-only copy.",
                confidence=0.88,
            )
        )
    if not evidence:
        issues.append(
            ReliabilityIssue(
                id=f"I{len(issues) + 1}",
                type="evaluation_limitation",
                severity="medium",
                title="No evidence ledger",
                description="No retrieved evidence was available for claim checking.",
                artifactIds=artifact_ids,
                suggestedFix="Run web_search or attach source-backed Research Artifacts before relying on this report.",
                confidence=0.95,
            )
        )
    return issues


def _score(issues: list[ReliabilityIssue]) -> int:
    total = 0
    weak_total = 0
    missing_source_total = 0
    unsupported_total = 0
    hallucinated_entity_total = 0
    no_evidence = any(issue.type == "evaluation_limitation" and issue.title == "No evidence ledger" for issue in issues)
    for issue in issues:
        weight = ISSUE_WEIGHTS[issue.type]
        if issue.type == "weakly_supported_claim":
            weak_total += weight
            continue
        if issue.type == "missing_source":
            missing_source_total += weight
            continue
        if issue.type == "unsupported_claim":
            unsupported_total += weight
            continue
        if issue.type == "hallucinated_entity":
            hallucinated_entity_total += weight
            continue
        total += weight
    total += min(weak_total, 20)
    total += min(missing_source_total, 25)
    if no_evidence:
        total += min(unsupported_total + hallucinated_entity_total, 40)
    else:
        total += min(unsupported_total, 36)
        total += min(hallucinated_entity_total, 30)
    return max(0, 100 - total)


def _status(score: int, issues: list[ReliabilityIssue]) -> str:
    if any(issue.type == "unsafe_action" for issue in issues):
        return "unsafe_to_ship"
    if any(issue.type == "mission_incomplete" for issue in issues):
        return "needs_human_review"
    if any(issue.type == "evaluation_limitation" and issue.title == "No evidence ledger" for issue in issues):
        return "needs_human_review"
    if any(issue.severity == "critical" for issue in issues):
        return "needs_human_review"
    if any(issue.severity == "high" for issue in issues):
        return "needs_human_review"
    if score >= 85:
        return "ship_ready"
    if score >= 70:
        return "minor_review"
    if score >= 50:
        return "needs_human_review"
    return "unsafe_to_ship"


def _gate_status(status_value: str, issues: list[ReliabilityIssue], detail: dict[str, Any]) -> str:
    actionable = [issue for issue in issues if issue.type != "mission_incomplete"]
    if status_value == "unsafe_to_ship" or any(issue.type == "unsafe_action" for issue in actionable):
        return "blocked"
    if any(issue.severity in {"critical", "high", "medium"} for issue in actionable):
        if any(issue.type == "evaluation_limitation" for issue in actionable):
            return "human_review"
        if _repeated_blocking_issue_count(detail, actionable) >= 2:
            return "human_review"
        return "repair_required"
    if status_value == "ship_ready":
        return "pass"
    if actionable:
        return "human_review"
    return "pass"


def _repeated_blocking_issue_count(detail: dict[str, Any], current_issues: list[ReliabilityIssue]) -> int:
    current_signatures = {
        _issue_signature(issue.model_dump(by_alias=True))
        for issue in current_issues
        if issue.severity in {"critical", "high", "medium"} and issue.type != "mission_incomplete"
    }
    if not current_signatures:
        return 0
    repeated_reports = 0
    for report in _historical_report_payloads(detail):
        previous_signatures = {
            _issue_signature(issue)
            for issue in report.get("issues", [])
            if isinstance(issue, dict)
            and issue.get("severity") in {"critical", "high", "medium"}
            and issue.get("type") != "mission_incomplete"
        }
        if current_signatures.intersection(previous_signatures):
            repeated_reports += 1
    return repeated_reports


def _historical_report_payloads(detail: dict[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for artifact in detail.get("artifacts", []):
        if artifact.get("metadata", {}).get("artifactRole") != "reliability_report":
            continue
        payload = artifact.get("metadata", {}).get("reportPayload")
        if isinstance(payload, dict):
            reports.append(payload)
    return reports


def _issue_signature(issue: dict[str, Any]) -> str:
    text = " ".join(
        str(issue.get(key) or "")
        for key in ("type", "title", "description")
    )
    text = URL_RE.sub(" ", text.lower())
    text = re.sub(r"\b[a-f0-9]{8,}\b", " ", text)
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:240]


def _summary(score: int, issues: list[ReliabilityIssue]) -> str:
    if not issues:
        return "No major reliability issues were detected from the available trace evidence."
    if any(issue.type == "evaluation_limitation" and issue.title == "No evidence ledger" for issue in issues):
        return f"Reliability score {score}. No trace evidence was available, so this research output needs human review."
    high = sum(1 for issue in issues if issue.severity in {"critical", "high"})
    return f"Reliability score {score}. Detected {len(issues)} issues, including {high} high-severity risks."


def _score_confidence(
    detail: dict[str, Any],
    evidence: list[EvidenceItem],
    issues: list[ReliabilityIssue],
) -> tuple[str, str]:
    mission_status = str(detail.get("mission", {}).get("status") or "")
    if not evidence:
        return "low", "No Evidence Ledger was available, so the score is a risk signal with limited factual coverage."
    if mission_status not in {"running", "completed"}:
        return "low", "The Mission is not in an active or completed state, so the report cannot certify the current candidate."
    if any(issue.type == "evaluation_limitation" for issue in issues):
        return "low", "Evaluator limitations remain in the current trace."
    if any(issue.severity in {"critical", "high"} for issue in issues):
        return "medium", "Evidence exists, but high-severity reliability issues remain unresolved."
    if any(issue.severity == "medium" for issue in issues):
        return "medium", "Evidence exists, but some claims or requirements still need review."
    return "high", "Visible trace evidence covers the evaluated candidate and no high-severity issue remains."


def _suggested_actions(issues: list[ReliabilityIssue]) -> list[str]:
    actions: list[str] = []
    for issue in issues:
        if issue.suggested_fix and issue.suggested_fix not in actions:
            actions.append(issue.suggested_fix)
        if len(actions) >= 5:
            break
    return actions


def _report_markdown(report: ReliabilityReport) -> str:
    lines = [
        "# Reliability Report",
        "",
        f"Score: {report.score} / 100",
        f"Status: {report.status}",
        f"Gate: {report.gate_status}",
        f"Evaluated Artifacts: {', '.join(report.evaluated_artifact_ids) or 'None'}",
        f"Meaning: {report.score_meaning}",
        f"Confidence: {report.confidence} - {report.confidence_reason}",
        f"Profile: {report.profile}",
        f"Mode: {report.mode}",
        "",
        report.summary,
        "",
        "## Tool Failures",
    ]
    if not report.tool_failures:
        lines.append("- None.")
    for failure in report.tool_failures:
        lines.append(
            f"- #{failure.event_sequence} {failure.tool}: {failure.code or failure.message} retryable={failure.retryable}"
        )
    lines.extend([
        "",
        "## Issues",
    ])
    if not report.issues:
        lines.append("- No open issues.")
    for issue in report.issues:
        lines.append(f"- [{issue.severity}] {issue.title}: {issue.description} Fix: {issue.suggested_fix}")
    lines.extend(["", "## Limitations"])
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines)


def _tool_failures(events: list[dict[str, Any]]) -> list[ToolFailureItem]:
    failures: list[ToolFailureItem] = []
    failed_types = {
        "WEB_SEARCH_FAILED": "web_search",
        "WORK_WINDOW_FAILED": "delegate_agent",
        "DISCUSSION_WINDOW_FAILED": "discuss_with_delegate",
        "MODEL_TURN_INVALID": "model_turn",
        "EVALUATION_FAILED": "evaluate_product",
    }
    for event in events:
        tool = str(event.get("payload", {}).get("tool") or failed_types.get(event.get("type"), ""))
        if not tool:
            continue
        is_failed = str(event.get("type") or "").endswith("_FAILED") or event.get("type") == "MODEL_TURN_INVALID"
        if not is_failed:
            continue
        payload = event.get("payload", {})
        failures.append(
            ToolFailureItem(
                id=f"TF{len(failures) + 1}",
                tool=tool,
                code=str(payload.get("code") or payload.get("error") or event.get("message") or "")[:120],
                message=str(event.get("message") or "")[:500],
                eventId=event["id"],
                eventSequence=event["sequence"],
                retryable=bool(payload.get("retryable", False)),
            )
        )
    return failures


def _issue_counts(issues: list[ReliabilityIssue]) -> dict[str, int]:
    counts = Counter(issue.severity for issue in issues)
    counts.update(f"type:{issue.type}" for issue in issues)
    return dict(counts)


def _with_replay_evidence(detail: dict[str, Any]) -> dict[str, Any]:
    if any(event.get("type") == "WEB_SEARCH_COMPLETED" for event in detail.get("events", [])):
        return detail
    replay_detail = {**detail, "events": list(detail.get("events", []))}
    replay_detail["events"].append(
        {
            "id": "replay_evidence_1",
            "userId": detail["mission"]["userId"],
            "missionId": detail["mission"]["id"],
            "runId": _latest_run_id(detail),
            "stepId": None,
            "sequence": 0,
            "type": "WEB_SEARCH_COMPLETED",
            "title": "Replay evidence",
            "message": "Deterministic replay evidence.",
            "payload": {
                "tool": "web_search",
                "status": "ok",
                "query": detail["mission"].get("goal", ""),
                "provider": "replay_fixture",
                "results": _replay_results(detail),
            },
            "createdAt": "",
        }
    )
    return replay_detail


def _evaluation_target(
    detail: dict[str, Any],
    product_ids: list[str] | None = None,
    artifact_ids: list[str] | None = None,
) -> dict[str, Any]:
    artifacts = [
        artifact
        for artifact in detail.get("artifacts", [])
        if artifact.get("metadata", {}).get("artifactRole") != "reliability_report"
    ]
    artifact_by_id = {artifact["id"]: artifact for artifact in artifacts}
    requested_product_ids = [str(value) for value in product_ids or [] if value]
    requested_artifact_ids = [str(value) for value in artifact_ids or [] if value]
    products = [
        product
        for product in detail.get("products", [])
        if not requested_product_ids or product.get("id") in set(requested_product_ids)
    ]
    target_artifacts: list[dict[str, Any]] = []
    selection_reason = "fallback"

    if requested_artifact_ids:
        target_artifacts = [
            artifact_by_id[artifact_id] for artifact_id in requested_artifact_ids if artifact_id in artifact_by_id
        ]
        selection_reason = "explicit_tool_args"
    elif products:
        deliverable_ids = [
            product.get("deliverableArtifactId")
            for product in products
            if product.get("deliverableArtifactId")
        ]
        target_artifacts = [
            artifact_by_id[artifact_id] for artifact_id in deliverable_ids if artifact_id in artifact_by_id
        ]
        selection_reason = "product_deliverable"
        if not target_artifacts:
            final_product_artifact_ids = {
                artifact_id
                for product in products
                if product.get("status") == "final"
                for artifact_id in product.get("artifactIds", [])
            }
            target_artifacts = [
                artifact for artifact in artifacts if artifact["id"] in final_product_artifact_ids
            ]
            selection_reason = "product_final"
    else:
        fallback = _final_artifact(detail)
        if fallback:
            target_artifacts = [fallback]
            selection_reason = "fallback_final_artifact"

    target_product_ids = requested_product_ids or _product_ids_for_artifacts(detail, [item["id"] for item in target_artifacts])
    target_artifacts = _dedupe_target_artifacts(target_artifacts)
    target_artifact_ids = [artifact["id"] for artifact in target_artifacts]
    return {
        "products": products,
        "artifacts": target_artifacts,
        "productIds": target_product_ids,
        "artifactIds": target_artifact_ids,
        "artifactHashes": {artifact["id"]: _artifact_hash(artifact) for artifact in target_artifacts},
        "selectionReason": selection_reason,
    }


def _dedupe_target_artifacts(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for artifact in artifacts:
        artifact_id = artifact.get("id")
        if not artifact_id or artifact_id in seen:
            continue
        seen.add(artifact_id)
        result.append(artifact)
    return result


def _product_ids_for_artifacts(detail: dict[str, Any], artifact_ids: list[str]) -> list[str]:
    wanted = set(artifact_ids)
    product_ids: list[str] = []
    for product in detail.get("products", []):
        product_artifact_ids = set(product.get("artifactIds") or [])
        if product.get("deliverableArtifactId"):
            product_artifact_ids.add(product["deliverableArtifactId"])
        if wanted.intersection(product_artifact_ids):
            product_ids.append(product["id"])
    return product_ids


def _artifact_hash(artifact: dict[str, Any]) -> str:
    normalized = _normalized_artifact_content(artifact)
    return sha256(normalized.encode("utf-8")).hexdigest()


def _normalized_artifact_content(artifact: dict[str, Any]) -> str:
    content = str(artifact.get("content") or "")
    return "\n".join(line.rstrip() for line in content.replace("\r\n", "\n").replace("\r", "\n").split("\n")).strip()


def _trace_snapshot(detail: dict[str, Any]) -> dict[str, int | str | None]:
    events = detail.get("events", [])
    product_sequences = [
        int(event.get("sequence") or 0)
        for event in events
        if event.get("type") in {"PRODUCT_UPDATED", "WORK_WINDOW_COMPLETED", "MISSION_COMPLETED"}
    ]
    search_sequences = [
        int(event.get("sequence") or 0)
        for event in events
        if event.get("type") in {"WEB_SEARCH_COMPLETED", "WEB_SEARCH_FAILED", "SEARCH_SUMMARY_CREATED"}
    ]
    return {
        "latestEventSequence": int(events[-1].get("sequence") or 0) if events else 0,
        "latestProductEventSequence": max(product_sequences) if product_sequences else None,
        "latestSearchEventSequence": max(search_sequences) if search_sequences else None,
        "evaluatorVersion": EVALUATOR_VERSION,
    }


def _replay_results(detail: dict[str, Any]) -> list[dict[str, Any]]:
    text = ""
    artifact = _final_artifact(detail)
    if artifact:
        text = artifact.get("content", "")
    mission_text = f"{detail['mission'].get('title', '')} {detail['mission'].get('goal', '')} {text}".lower()
    if "海地" in mission_text or "haiti" in mission_text:
        return [
            {
                "title": "Haitian Revolution reference",
                "url": "https://www.britannica.com/event/Haitian-Revolution",
                "source": "britannica.com",
                "snippet": "The Haitian Revolution was a conflict in Saint-Domingue that led to Haitian independence and reshaped Atlantic politics.",
                "publishedAt": None,
            }
        ]
    return [
        {
            "title": "Cohere enterprise AI",
            "url": "https://cohere.com",
            "source": "cohere.com",
            "snippet": "Cohere provides enterprise AI models and is headquartered in Toronto.",
            "publishedAt": None,
        },
        {
            "title": "Layer 6 AI",
            "url": "https://www.layer6.ai",
            "source": "layer6.ai",
            "snippet": "Layer 6 applies machine learning and AI research in Toronto.",
            "publishedAt": None,
        },
        {
            "title": "Vector Institute startup ecosystem",
            "url": "https://vectorinstitute.ai",
            "source": "vectorinstitute.ai",
            "snippet": "Toronto has a large AI ecosystem connected to enterprise AI research and startups.",
            "publishedAt": None,
        },
    ]


def _artifact_sources(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = artifact.get("metadata", {})
    role = metadata.get("artifactRole")
    sources = metadata.get("sources") or metadata.get("sourceUrls") or metadata.get("evidence")
    normalized_sources: list[dict[str, Any]] = []
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, dict) and source.get("url"):
                normalized_sources.append(source)
            elif isinstance(source, str) and source.startswith("http"):
                normalized_sources.append({"url": source, "title": source, "snippet": artifact.get("content", "")[:1200]})
    elif isinstance(sources, dict) and sources.get("url"):
        normalized_sources.append(sources)
    if normalized_sources:
        return normalized_sources
    if role in {"research_evidence", "source", "evidence"}:
        urls = URL_RE.findall(str(artifact.get("content") or ""))
        if urls:
            return [
                {"url": url, "title": artifact.get("title", ""), "snippet": artifact.get("content", "")[:1200]}
                for url in urls[:5]
            ]
    return []


def _source_from_url(url: Any) -> str:
    if not url:
        return ""
    try:
        return urlparse(str(url)).netloc
    except ValueError:
        return ""


def _final_artifact(detail: dict[str, Any]) -> dict[str, Any] | None:
    artifacts = [
        artifact
        for artifact in detail.get("artifacts", [])
        if artifact.get("metadata", {}).get("artifactRole") != "reliability_report"
    ]
    deliverable_ids = [
        product.get("deliverableArtifactId")
        for product in detail.get("products", [])
        if product.get("deliverableArtifactId")
    ]
    for artifact_id in deliverable_ids:
        artifact = next((item for item in artifacts if item["id"] == artifact_id), None)
        if artifact:
            return artifact
    final_ids = _final_artifact_ids(detail.get("events", []))
    for artifact_id in final_ids:
        artifact = next((item for item in artifacts if item["id"] == artifact_id), None)
        if artifact:
            return artifact
    final_artifact = next((item for item in artifacts if item.get("kind") == "final"), None)
    if final_artifact:
        return final_artifact
    product_artifact_ids = {
        artifact_id
        for product in detail.get("products", [])
        if product.get("status") == "final"
        for artifact_id in product.get("artifactIds", [])
    }
    for artifact in artifacts:
        if artifact["id"] in product_artifact_ids:
            return artifact
    return artifacts[0] if artifacts else None


def _final_artifact_ids(events: list[dict[str, Any]]) -> list[str]:
    for event in reversed(events):
        if event.get("type") == "MISSION_COMPLETED":
            return list(event.get("payload", {}).get("finalArtifactIds") or [])
    return []


def _latest_run_id(detail: dict[str, Any]) -> str | None:
    active = detail.get("activeRun")
    latest = detail.get("latestRun")
    return (active or latest or {}).get("id")


def _latest_event_is_current_report(detail: dict[str, Any], target: dict[str, Any]) -> bool:
    events = detail.get("events", [])
    if not events:
        return False
    latest = events[-1]
    if latest.get("type") != "RELIABILITY_REPORTED":
        return False
    payload = latest.get("payload", {})
    if payload.get("evaluatorVersion") != EVALUATOR_VERSION:
        return False
    report_artifact_id = str(payload.get("reportArtifactId") or "")
    if not report_artifact_id:
        return False
    report_artifact = next(
        (
            artifact
            for artifact in detail.get("artifacts", [])
            if artifact.get("id") == report_artifact_id
            and artifact.get("metadata", {}).get("artifactRole") == "reliability_report"
        ),
        None,
    )
    report = report_artifact.get("metadata", {}).get("reportPayload") if report_artifact else None
    if not isinstance(report, dict):
        return False
    return _report_matches_target(report, target)


def _report_matches_target(report: dict[str, Any], target: dict[str, Any]) -> bool:
    expected_ids = set(target.get("artifactIds") or [])
    report_ids = set(report.get("evaluatedArtifactIds") or [])
    if expected_ids != report_ids:
        return False
    report_hashes = report.get("evaluatedArtifactHashes") or {}
    if not isinstance(report_hashes, dict):
        return False
    for artifact_id, artifact_hash in (target.get("artifactHashes") or {}).items():
        if report_hashes.get(artifact_id) != artifact_hash:
            return False
    return True


def _expected_count(goal: str) -> int | None:
    digit = re.search(r"\b([2-9]|10)\b", goal)
    if digit and re.search(r"\b(compan|startups?|companies|firms|entities|sources)\b", goal):
        return int(digit.group(1))
    words = {"two": 2, "three": 3, "four": 4, "five": 5}
    for word, count in words.items():
        if word in goal and re.search(r"\b(compan|startups?|companies|firms|entities|sources)\b", goal):
            return count
    return None


def _expected_word_count(text: str) -> int | None:
    matches = re.findall(r"\b([1-9]\d{2,5})\s*(?:-?\s*)?(?:words?|word|词)\b", text, flags=re.IGNORECASE)
    if not matches:
        return None
    expected = max(int(match) for match in matches)
    return expected if expected >= 100 else None


def _content_word_count(text: str) -> int:
    content = URL_RE.sub(" ", _claim_body_text(text))
    return len(WORD_RE.findall(content))


def _count_requirement_status(actual: int, expected: int) -> str:
    if actual >= expected:
        return "met"
    if actual >= max(1, int(expected * 0.8)):
        return "partially_met"
    return "missing"


def _expected_long_form_source_count(
    requirement_text: str,
    expected_words: int | None,
    paper_like: bool,
) -> int | None:
    if not paper_like or expected_words is None or expected_words < 1500:
        return None
    lowered = requirement_text.lower()
    if "literature review" in lowered or "文献综述" in lowered or "historiograph" in lowered:
        return max(6, min(16, expected_words // 1000))
    return max(4, min(10, expected_words // 1500))


def _expected_long_form_domain_count(expected_sources: int) -> int:
    return max(3, min(6, (expected_sources + 1) // 2))


def _unique_evidence_url_count(evidence: list[EvidenceItem]) -> int:
    urls = {item.url.strip().lower().rstrip("/.") for item in evidence if item.url.strip()}
    return len(urls)


def _unique_evidence_domain_count(evidence: list[EvidenceItem]) -> int:
    domains = {_source_from_url(item.url).lower().removeprefix("www.") for item in evidence if item.url.strip()}
    return len({domain for domain in domains if domain})


def _body_source_marker_count(text: str) -> int:
    body = _claim_body_text(text)
    urls = URL_RE.findall(body)
    author_year = re.findall(r"\([A-Z][A-Za-z& .'-]{1,80},\s*(?:n\.d\.|\d{4}[a-z]?)\)", body)
    bracketed_numbers = re.findall(r"\[(?:\d{1,3}|[A-Za-z][A-Za-z0-9_-]{1,30})\]", body)
    return len(urls) + len(author_year) + len(bracketed_numbers)


def _requires_english(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in ("english", "英文", "英语"))


def _english_requirement(text: str) -> tuple[str, str]:
    cjk_count = len(CHINESE_CHAR_RE.findall(text))
    word_count = _content_word_count(text)
    if word_count >= 80 and cjk_count <= 30:
        return "met", f"Detected {word_count} English-like words and {cjk_count} CJK characters."
    if word_count >= 40:
        return "partially_met", f"Detected only {word_count} English-like words and {cjk_count} CJK characters."
    return "missing", f"Detected only {word_count} English-like words and {cjk_count} CJK characters."


def _requires_apa(text: str) -> bool:
    return "apa" in text.lower()


def _apa_requirement(text: str) -> tuple[str, str]:
    has_references = bool(re.search(r"(?im)^\s{0,3}(?:#{1,6}\s*)?references\s*:?\s*$", text))
    has_parenthetical = bool(re.search(r"\([A-Z][A-Za-z& .'-]{1,80},\s*(?:n\.d\.|\d{4}[a-z]?)\)", text))
    has_author_year_reference = bool(APA_REFERENCE_RE.search(text))
    if has_references and (has_parenthetical or has_author_year_reference):
        return "met", "Detected References section and APA-style author/date citation shape."
    if has_references or has_parenthetical or has_author_year_reference:
        return "partially_met", "Detected only partial APA citation shape."
    return "missing", "No APA-style References section or author/date citation shape was detected."


def _entities(text: str) -> list[str]:
    found: list[str] = []
    text_without_urls = URL_RE.sub(" ", text)
    stop_entities = {item.lower() for item in STOP_ENTITIES}
    for match in ENTITY_RE.finditer(text_without_urls):
        entity = " ".join(match.group(0).split()).strip(" .:-")
        entity_lower = entity.lower()
        if len(entity) < 3 or entity_lower in stop_entities:
            continue
        if _looks_url_slug_entity(entity):
            continue
        if entity_lower in {item.lower() for item in found}:
            continue
        found.append(entity)
    return found[:20]


def _best_entity(sentence: str) -> str:
    entities = _entities(sentence)
    return entities[0] if entities else ""


def _sentences(text: str) -> list[str]:
    return [item.strip(" -•\t") for item in SENTENCE_RE.split(text) if len(item.strip()) >= 20]


def _claim_body_text(text: str) -> str:
    body_lines: list[str] = []
    for line in text.splitlines():
        if REFERENCE_HEADING_RE.match(line) or EVIDENCE_LEDGER_HEADING_RE.match(line):
            break
        body_lines.append(line)
    return "\n".join(body_lines)


def _is_reference_like_sentence(sentence: str) -> bool:
    stripped = sentence.strip(" -•\t")
    lowered = stripped.lower()
    if not stripped:
        return True
    if REFERENCE_HEADING_RE.match(stripped):
        return True
    if EVIDENCE_LEDGER_HEADING_RE.match(stripped):
        return True
    if APA_REFERENCE_RE.match(stripped):
        return True
    if lowered.startswith(("source:", "sources:", "reference:", "references:", "url:", "link:", "doi:")):
        return True
    if URL_RE.fullmatch(stripped):
        return True
    if URL_RE.match(stripped):
        remainder = URL_RE.sub(" ", stripped)
        return len(WORD_RE.findall(remainder)) <= 4
    return False


def _looks_url_slug_entity(entity: str) -> bool:
    lowered = entity.lower()
    return (
        "http" in lowered
        or "www" in lowered
        or "/" in entity
        or "." in entity
        or entity.count("-") >= 2
    )


def _looks_factual(sentence: str) -> bool:
    lowered = sentence.lower()
    factual_terms = (
        "based",
        "build",
        "company",
        "customers",
        "enterprise",
        "founded",
        "headquartered",
        "located",
        "offers",
        "platform",
        "startup",
        "toronto",
        "works with",
        "revolution",
        "war",
        "government",
        "history",
        "革命",
        "战争",
        "政府",
        "殖民",
        "历史",
        "研究",
        "数据显示",
        "根据",
        "位于",
        "成立",
        "影响",
    )
    return any(term in lowered for term in factual_terms) and not lowered.startswith(("subject:", "dear "))


def _claim_type(sentence: str) -> str:
    lowered = sentence.lower()
    if "based" in lowered or "headquartered" in lowered or "located" in lowered or "toronto" in lowered:
        return "location"
    if "customer" in lowered or "banks" in lowered or "fortune" in lowered:
        return "customer"
    if "founded" in lowered:
        return "founding"
    if "build" in lowered or "platform" in lowered or "offers" in lowered:
        return "product"
    return "other"


def _support(claim: str, entity: str, evidence: list[EvidenceItem]) -> tuple[str, list[str], float, str]:
    if not evidence:
        return "not_evaluable", [], 0.0, "No evidence was available."
    claim_tokens = _tokens(claim)
    best: tuple[int, EvidenceItem | None] = (0, None)
    entity_lower = entity.lower()
    for item in evidence:
        text = f"{item.title} {item.snippet} {item.source}".lower()
        overlap = len(claim_tokens.intersection(_tokens(text)))
        if entity_lower and entity_lower in text:
            overlap += 2
        if overlap > best[0]:
            best = (overlap, item)
    if best[1] is None or best[0] == 0:
        return "none", [], 0.82, "No evidence item overlaps with the claim."
    evidence_id = best[1].id
    if best[0] >= 4:
        return "strong", [evidence_id], 0.9, "Evidence directly overlaps with the claim."
    if best[0] >= 2:
        return "weak", [evidence_id], 0.68, "Evidence mentions related facts but is not specific enough."
    return "none", [], 0.78, "Evidence overlap is too weak to support the claim."


def _tokens(text: str) -> set[str]:
    text = URL_RE.sub(" ", text)
    tokens = {
        token.lower()
        for token in WORD_RE.findall(text)
        if len(token) > 3 and token.lower() not in STOP_WORDS
    }
    if CHINESE_CHAR_RE.search(text):
        tokens.update(_chinese_bigrams(text))
    return tokens


def is_research_paper_like_goal(goal: str) -> bool:
    text = goal.lower()
    paper_terms = (
        "论文",
        "文献综述",
        "研究报告",
        "研究论文",
        "学术",
        "essay",
        "paper",
        "research paper",
        "literature review",
        "research report",
    )
    return any(term in text for term in paper_terms)


def artifact_is_research_paper_final_draft(artifact: dict[str, Any] | None) -> bool:
    if not artifact:
        return False
    title = str(artifact.get("title") or "")
    kind = str(artifact.get("kind") or "")
    content = str(artifact.get("content") or "")
    if kind == "outline":
        return False
    if _looks_like_outline_or_plan(title) and kind not in {"final", "report"}:
        return False
    cjk_count = len(CHINESE_CHAR_RE.findall(content))
    word_count = len(WORD_RE.findall(content))
    if cjk_count < 180 and word_count < 220:
        return False
    if _looks_like_outline_or_plan(content) and not _has_body_prose_shape(content):
        return False
    if kind not in {"final", "report", "draft", "revision"}:
        return False
    return _has_body_prose_shape(content)


def _looks_like_outline_or_plan(text: str) -> bool:
    normalized = text.lower()
    outline_terms = (
        "大纲",
        "提纲",
        "计划",
        "蓝图",
        "执行计划",
        "章节规划",
        "结构",
        "outline",
        "plan",
        "blueprint",
    )
    if any(term in normalized for term in outline_terms):
        return True
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    bulletish = sum(1 for line in lines if re.match(r"^([0-9一二三四五六七八九十]+[、.)．]|[-*•])", line))
    return len(lines) >= 3 and bulletish / len(lines) >= 0.6


def _has_body_prose_shape(text: str) -> bool:
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    long_paragraphs = [
        item
        for item in paragraphs
        if len(CHINESE_CHAR_RE.findall(item)) >= 45 or len(WORD_RE.findall(item)) >= 55
    ]
    if len(long_paragraphs) >= 2:
        return True
    return bool(re.search(r"(引言|正文|结论|第一部分|第二部分|introduction|conclusion)", text, re.IGNORECASE)) and (
        len(CHINESE_CHAR_RE.findall(text)) >= 220 or len(WORD_RE.findall(text)) >= 260
    )


def _chinese_bigrams(text: str) -> set[str]:
    chars = CHINESE_CHAR_RE.findall(text)
    return {"".join(chars[index : index + 2]) for index in range(max(len(chars) - 1, 0))}


def _all_evidence_text(evidence: list[EvidenceItem]) -> str:
    return " ".join(f"{item.title} {item.snippet} {item.source}" for item in evidence).lower()


def _requirement_fix(requirement: RequirementItem) -> str:
    if requirement.field_name == "source link":
        return "Add one trace-backed source link for each researched entity."
    if requirement.field_name == "word count":
        return f"Expand the deliverable body to at least {requirement.expected_count} words before references."
    if requirement.field_name == "source depth":
        return f"Search, read, and cite at least {requirement.expected_count} trace-backed sources before re-evaluating."
    if requirement.field_name == "source diversity":
        return f"Add sources from at least {requirement.expected_count} distinct credible domains or publishers."
    if requirement.field_name == "source density":
        return f"Distribute at least {requirement.expected_count} source or citation markers through the body prose, not only in an Evidence Ledger."
    if requirement.field_name == "language":
        return "Rewrite the deliverable in the requested language."
    if requirement.field_name == "APA format":
        return "Add APA-style in-text citations and a References section, or revise existing citations to APA shape."
    if requirement.expected_count:
        return f"Revise the final answer to include {requirement.expected_count} researched entities."
    return "Revise the final answer to satisfy this requirement."


def _employee_payload(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission.get("leadEmployeeId") or mission.get("lead_employee_id") or "employee_default_lead",
        "name": mission.get("leadEmployeeName") or mission.get("lead_employee_name") or "Lead",
        "role": mission.get("leadEmployeeRole") or mission.get("lead_employee_role") or "Mission lead",
    }
