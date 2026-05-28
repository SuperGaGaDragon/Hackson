"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status

from work_mode.evaluator_schemas import (
    ClaimItem,
    EvidenceItem,
    EvaluationProfile,
    ReliabilityIssue,
    ReliabilityReport,
    RequirementItem,
)
from work_mode.service import WorkModeService

ISSUE_WEIGHTS = {
    "missing_requirement": 15,
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
EVALUATOR_VERSION = "2026-05-28.research-paper-gate.v2"
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9&.-]*")
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")
CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")
ENTITY_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9&.-]+(?:\s+|$)){1,4}(?:AI|Labs|Systems|Technologies|Tech|Inc|Corp|Company|Cohere|Layer|Vector)?")
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
    ) -> dict[str, Any]:
        detail = self.service.get_mission_detail(user_id, mission_id)
        run_id = _latest_run_id(detail)
        if run_id is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mission_has_no_run")
        if _latest_event_is_current_report(detail):
            return detail
        report = build_reliability_report(detail, profile=profile)
        artifact = self._persist_report(user_id, mission_id, run_id, report)
        report.report_artifact_id = artifact["id"]
        mission = self.service._require_mission(user_id, mission_id)
        self.service.append_event(
            user_id,
            mission,
            run={"_id": run_id},
            step=None,
            event_type="RELIABILITY_REPORTED",
            title="Reliability",
            message=f"{report.score} / 100",
            payload={
                "profile": report.profile,
                "score": report.score,
                "status": report.status,
                "issueCounts": report.issue_counts,
                "reportArtifactId": artifact["id"],
                "evaluatorVersion": EVALUATOR_VERSION,
                "employee": _employee_payload(detail["mission"]),
            },
        )
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
) -> ReliabilityReport:
    mission = detail["mission"]
    final_artifact = _final_artifact(detail)
    final_text = final_artifact.get("content", "") if final_artifact else ""
    evidence = _evidence_ledger(detail.get("events", []))
    goal = mission.get("goal", "")
    requirements = _requirements(goal, final_text, evidence, final_artifact)
    claims = _claims(final_text, final_artifact["id"] if final_artifact else "", evidence)
    issues = _issues(detail, requirements, claims, evidence, final_artifact)
    score = _score(issues)
    report = ReliabilityReport(
        reportId=f"report_{uuid4().hex[:12]}",
        missionId=mission["id"],
        profile=profile,
        score=score,
        status=_status(score, issues),
        summary=_summary(score, issues),
        requirements=requirements,
        claims=claims,
        evidence=evidence,
        issues=issues,
        issueCounts=dict(Counter(issue.severity for issue in issues)),
        suggestedNextActions=_suggested_actions(issues),
        limitations=[
            "Evidence support is limited to Work Mode search results and source snippets in the Mission trace.",
            "The score is a triage signal, not a proof of correctness.",
        ],
    )
    return report


def _evidence_ledger(events: list[dict[str, Any]]) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
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
    return evidence


def _requirements(
    goal: str,
    final_text: str,
    evidence: list[EvidenceItem],
    final_artifact: dict[str, Any] | None = None,
) -> list[RequirementItem]:
    lowered = goal.lower()
    requirements: list[RequirementItem] = []
    expected_count = _expected_count(lowered)
    final_entities = _entities(final_text)
    url_count = len(URL_RE.findall(final_text))
    paper_like = is_research_paper_like_goal(goal)
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
    for sentence in _sentences(final_text):
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
    if mission_status != "completed":
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
    for issue in issues:
        weight = ISSUE_WEIGHTS[issue.type]
        if issue.type == "weakly_supported_claim":
            weak_total += weight
            continue
        if issue.type == "missing_source":
            missing_source_total += weight
            continue
        total += weight
    total += min(weak_total, 20)
    total += min(missing_source_total, 25)
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
    if score >= 85:
        return "ship_ready"
    if score >= 70:
        return "minor_review"
    if score >= 50:
        return "needs_human_review"
    return "unsafe_to_ship"


def _summary(score: int, issues: list[ReliabilityIssue]) -> str:
    if not issues:
        return "No major reliability issues were detected from the available trace evidence."
    if any(issue.type == "evaluation_limitation" and issue.title == "No evidence ledger" for issue in issues):
        return f"Reliability score {score}. No trace evidence was available, so this research output needs human review."
    high = sum(1 for issue in issues if issue.severity in {"critical", "high"})
    return f"Reliability score {score}. Detected {len(issues)} issues, including {high} high-severity risks."


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
        f"Profile: {report.profile}",
        "",
        report.summary,
        "",
        "## Issues",
    ]
    if not report.issues:
        lines.append("- No open issues.")
    for issue in report.issues:
        lines.append(f"- [{issue.severity}] {issue.title}: {issue.description} Fix: {issue.suggested_fix}")
    lines.extend(["", "## Limitations"])
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines)


def _final_artifact(detail: dict[str, Any]) -> dict[str, Any] | None:
    artifacts = [
        artifact
        for artifact in detail.get("artifacts", [])
        if artifact.get("metadata", {}).get("artifactRole") != "reliability_report"
    ]
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


def _latest_event_is_current_report(detail: dict[str, Any]) -> bool:
    events = detail.get("events", [])
    if not events:
        return False
    latest = events[-1]
    if latest.get("type") != "RELIABILITY_REPORTED":
        return False
    payload = latest.get("payload", {})
    return payload.get("evaluatorVersion") == EVALUATOR_VERSION


def _expected_count(goal: str) -> int | None:
    digit = re.search(r"\b([2-9]|10)\b", goal)
    if digit and re.search(r"\b(compan|startups?|companies|firms|entities|sources)\b", goal):
        return int(digit.group(1))
    words = {"two": 2, "three": 3, "four": 4, "five": 5}
    for word, count in words.items():
        if word in goal and re.search(r"\b(compan|startups?|companies|firms|entities|sources)\b", goal):
            return count
    return None


def _entities(text: str) -> list[str]:
    found: list[str] = []
    for match in ENTITY_RE.finditer(text):
        entity = " ".join(match.group(0).split()).strip(" .:-")
        if len(entity) < 3 or entity in STOP_ENTITIES:
            continue
        if entity.lower() in {item.lower() for item in found}:
            continue
        found.append(entity)
    return found[:20]


def _best_entity(sentence: str) -> str:
    entities = _entities(sentence)
    return entities[0] if entities else ""


def _sentences(text: str) -> list[str]:
    return [item.strip(" -•\t") for item in SENTENCE_RE.split(text) if len(item.strip()) >= 20]


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
        "source",
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
    if requirement.expected_count:
        return f"Revise the final answer to include {requirement.expected_count} researched entities."
    return "Revise the final answer to satisfy this requirement."


def _employee_payload(mission: dict[str, Any]) -> dict[str, str]:
    return {
        "id": mission.get("leadEmployeeId") or mission.get("lead_employee_id") or "employee_default_lead",
        "name": mission.get("leadEmployeeName") or mission.get("lead_employee_name") or "Lead",
        "role": mission.get("leadEmployeeRole") or mission.get("lead_employee_role") or "Mission lead",
    }
