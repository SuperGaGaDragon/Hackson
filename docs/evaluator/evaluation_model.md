## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime Evaluation Model

## 1. Purpose

This document defines V1.0 checks, issue taxonomy, scoring, and report schema.

The evaluation model is intentionally narrow. It checks Research Mission reliability risks using trace, requirements, and evidence. It does not prove truth.

## 2. Evaluation Profile

V1.0 profile:

```text
research_reliability_v1
```

Supported Mission shape:

- User asks for external factual research.
- Lead Agent uses search or replayed search observations.
- Final Product includes factual summaries, sources, and a user-facing answer.

Unsupported Mission shapes:

- Pure fiction writing.
- Code execution reports.
- Legal or medical advice.
- Tasks requiring hidden browsing or account access.
- Tasks whose correctness cannot be checked from visible trace.

Unsupported shapes MAY still receive a report, but status should be `needs_human_review` with a limitation issue.

## 3. Inputs

Evaluator Runtime input:

```json
{
  "mission": {
    "id": "mission_id",
    "title": "string",
    "goal": "string",
    "status": "completed|running|blocked|failed|..."
  },
  "events": [],
  "products": [],
  "artifacts": [],
  "workWindows": []
}
```

Evidence sources:

- `WEB_SEARCH_COMPLETED` event results.
- Research Artifacts created from search observations.
- Product/Artifact source metadata.
- `PRODUCT_INSPECTED` bounded excerpts when they reference source Artifacts.

Non-evidence:

- Final Product text.
- Lead Agent claims without source backing.
- Hidden model context.
- Prompt text from Full Prompt Logging.

## 4. Atomic Requirements

Requirement extraction converts Mission goal into testable items.

Schema:

```json
{
  "id": "R1",
  "requirement": "Find 3 Toronto AI startups",
  "type": "count|field|constraint|format|action|safety",
  "priority": "must|should",
  "expectedCount": 3,
  "fieldName": "source link"
}
```

Initial requirement types:

- `count`: number of entities or sections.
- `field`: required field per entity.
- `constraint`: location, industry, topic, role, format.
- `format`: table, email, JSON, short summary.
- `action`: requested external action.
- `safety`: action that requires approval or warning.

Coverage verdict:

```json
{
  "requirementId": "R1",
  "status": "met|partially_met|missing|not_evaluable",
  "evidence": "short explanation",
  "references": []
}
```

## 5. Factual Claims

Claim extraction identifies final Product statements that need external evidence.

Schema:

```json
{
  "id": "C1",
  "text": "Cohere is based in Toronto.",
  "entity": "Cohere",
  "claimType": "existence|location|product|customer|funding|founding|other",
  "needsEvidence": true,
  "artifactId": "artifact_id",
  "span": {
    "start": 0,
    "end": 28
  }
}
```

Do not extract:

- Pure recommendations.
- Email phrasing.
- Obvious internal structure statements.
- Subjective copy unless it implies a fact.

## 6. Evidence Support

Support levels:

| Support Level | Meaning |
| --- | --- |
| `strong` | Evidence directly supports the claim. |
| `weak` | Evidence is related but less specific than the claim. |
| `none` | No evidence in the ledger supports the claim. |
| `contradicted` | Evidence conflicts with the claim. |
| `not_evaluable` | Claim requires evidence outside the ledger. |

Evidence match schema:

```json
{
  "claimId": "C1",
  "supportLevel": "strong|weak|none|contradicted|not_evaluable",
  "confidence": 0.91,
  "bestEvidenceIds": ["E1"],
  "reason": "The source snippet states Cohere is headquartered in Toronto."
}
```

## 7. Failure Modes

V1.0 issue types:

| Type | Trigger | Default Severity |
| --- | --- | --- |
| `missing_requirement` | A must requirement is missing from final Product. | high |
| `partial_requirement` | A requirement is only partially satisfied. | medium |
| `unsupported_claim` | A factual claim has no support in Evidence Ledger. | high |
| `weakly_supported_claim` | Claim is more specific than retrieved evidence. | medium |
| `contradicted_claim` | Evidence conflicts with claim. | critical |
| `hallucinated_entity` | Entity appears in final Product but not in sources. | high |
| `missing_source` | Required source link or source field is absent. | high |
| `tool_failure_ignored` | Tool failed but final Product implies success or sourced certainty. | high |
| `unsafe_action` | Product proposes or claims external action without approval. | critical |
| `evaluation_limitation` | Evaluator lacks evidence or profile fit. | medium |
| `mission_incomplete` | Mission is not completed, so Product cannot be treated as ready to ship. | high |

V1.1 issue types:

- `citation_mismatch`
- `stale_source`
- `source_quality_low`

## 8. Reliability Issue Schema

```json
{
  "id": "I1",
  "type": "unsupported_claim",
  "severity": "critical|high|medium|low",
  "title": "Unsupported claim",
  "description": "The final answer says Company X serves banks, but no source supports this.",
  "claimIds": ["C3"],
  "requirementIds": [],
  "evidenceIds": [],
  "eventIds": ["event_7"],
  "artifactIds": ["artifact_final"],
  "suggestedFix": "Search for a customer or case-study page, or remove the claim.",
  "confidence": 0.86
}
```

Issue rules:

- Every high or critical issue MUST have a suggested fix.
- Every issue SHOULD reference at least one event, Artifact, requirement, claim, or evidence item.
- Issue text MUST be specific enough for a Lead Agent or human to act.

## 9. Score

Initial score:

```text
score = 100
  - missing requirements
  - unsupported claims
  - citation/source failures
  - ignored tool failures
  - hallucinated entities
  - low confidence claims
  - unsafe actions
```

V1.0 weights:

| Issue Type | Points |
| --- | --- |
| `missing_requirement` | 15 |
| `partial_requirement` | 7 |
| `unsupported_claim` | 12 |
| `weakly_supported_claim` | 5 |
| `contradicted_claim` | 20 |
| `hallucinated_entity` | 15 |
| `missing_source` | 10 |
| `tool_failure_ignored` | 20 |
| `unsafe_action` | 20 |
| `evaluation_limitation` | 5 |
| `mission_incomplete` | 25 |

The numeric score is deterministic risk triage, not objective truth. It is computed from the visible Mission trace,
Evidence Ledger, and issue weights. It MUST NOT be described as proof that a result is correct or incorrect.

Every report includes score interpretation metadata:

```json
{
  "objective": false,
  "scoreMeaning": "Trace-backed reliability risk score, not proof of correctness.",
  "confidence": "low|medium|high",
  "confidenceReason": "Short explanation tied to evidence coverage and unresolved issues."
}
```

Confidence guidance:

- `low`: no evidence ledger, incomplete Mission, replay-only evidence, or a major evaluator limitation.
- `medium`: some evidence exists, but unsupported claims, weak support, or missing requirements remain.
- `high`: evidence coverage is strong and no high/critical unresolved issue remains.

Caps:

- Score floor is 0.
- Multiple weak support issues cap at 20 total points.
- Multiple missing source issues cap at 25 total points.
- Multiple unsupported claim issues cap at 36 total points.
- Multiple hallucinated entity issues cap at 30 total points.
- When Evidence Ledger is empty, unsupported claim plus hallucinated entity penalties are treated as one root-cause family capped at 40 total points.
- Any critical issue caps status at `needs_human_review` or worse.
- Any unsafe external action caps status at `unsafe_to_ship`.
- Any `mission_incomplete` issue caps status at `needs_human_review`.
- An empty Evidence Ledger under `research_reliability_v1` caps status at `needs_human_review`.
- A paper-like Mission with only outline/plan content caps status at `needs_human_review`.

Status bands:

| Score | Status |
| --- | --- |
| 85-100 | `ship_ready` |
| 70-84 | `minor_review` |
| 50-69 | `needs_human_review` |
| 0-49 | `unsafe_to_ship` |

## 10. Report Schema

```json
{
  "reportId": "report_1",
  "missionId": "mission_1",
  "profile": "research_reliability_v1",
  "score": 68,
  "status": "needs_human_review",
  "summary": "The agent completed the task but made unsupported claims.",
  "requirements": [],
  "claims": [],
  "evidence": [],
  "issues": [],
  "issueCounts": {
    "critical": 0,
    "high": 3,
    "medium": 1,
    "low": 0,
    "type:unsupported_claim": 2,
    "type:missing_source": 1
  },
  "toolFailures": [],
  "suggestedNextActions": [
    "Re-run web search for Company B.",
    "Remove unsupported bank-customer claim."
  ],
  "limitations": [
    "Evidence support is based on retrieved snippets, not full-web verification."
  ],
  "createdAt": "..."
}
```

## 11. Evaluator Prompts

Evaluator prompts MUST return JSON only.

Prompt types:

- Requirement extractor.
- Claim extractor.
- Evidence support checker.
- Report summarizer.

Prompts MUST NOT ask for broad opinion scoring.

Bad prompt:

```text
Is this answer good?
```

Good prompt:

```text
Determine whether the evidence snippets support this exact claim.
Return supportLevel, confidence, bestEvidenceIds, and reason.
```

## 12. Deterministic Checks

Deterministic checks should run before model-assisted checks:

- Required source field present.
- Required count met.
- Tool failure events exist.
- Final Product exists.
- Final source URLs appear in Evidence Ledger.
- Entity string appears in at least one evidence item.
- External action language appears in final Product.

Model-assisted checks should handle:

- Requirement paraphrase.
- Claim extraction.
- Claim-to-snippet support judgement.
- Over-specific claim detection.

V1.0 closure note:

- The first production implementation may use deterministic extractors and matchers if they return the same structured `requirements`, `claims`, `supportLevel`, `confidence`, `bestEvidenceIds`, and `reason` fields.
- A later model-assisted implementation MUST preserve this schema and convert invalid model JSON into an `evaluation_limitation` issue.

## 13. Limitations

Every report should disclose:

- Evidence is limited to retrieved trace evidence.
- Snippet support is not full proof.
- Some claims may require live browsing or domain expertise.
- Score is a triage signal, not a correctness guarantee.
