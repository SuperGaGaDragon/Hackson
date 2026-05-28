## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime Implementation Plan

## 1. Purpose

This document is the engineer-facing build order for V1.0 Research Reliability Report.

Follow this plan after reading:

1. `README.md`
2. `final_version.md`
3. `architecture.md`
4. `evaluation_model.md`
5. `state_machine.md`
6. `ui_contract.md`
7. linked `issues/*.md`

## 2. Build Principles

- Start with trace-backed deterministic checks.
- Add model-assisted checks only with strict JSON schemas.
- Keep the first supported profile narrow: `research_reliability_v1`.
- Preserve Work Mode's Product and Artifact lineage.
- Use replay data for deterministic demo before relying on live search.
- Do not create a separate app unless Work Console cannot carry the report.

## 3. Loop 1: Report Schemas

Files:

- `backend/work_mode/evaluator_schemas.py`
- tests under `backend/work_mode/tests/`

Implement:

- `EvaluationRun`
- `ReliabilityReport`
- `ReliabilityIssue`
- `RequirementItem`
- `ClaimItem`
- `EvidenceItem`
- enums for profile, status, severity, issue type, support level.

Tests:

- Valid report schema.
- Invalid score rejected.
- Unknown issue type rejected.
- High severity issue requires suggested fix.

Acceptance:

- Report payload can be serialized as JSON and stored in Artifact metadata.

## 4. Loop 2: Trace Reader And Evidence Ledger

Files:

- `backend/work_mode/evaluator.py`

Implement:

- Read Mission detail.
- Normalize Work events into trace steps.
- Extract `WEB_SEARCH_COMPLETED` results when present.
- Extract fake replay search observations for smoke.
- Build Evidence Ledger.

Tests:

- Search event results become Evidence Items.
- Final Product text is not treated as evidence.
- Failed tool events are preserved.
- Evidence item references source event sequence.

Acceptance:

- A seeded Mission detail produces a deterministic Evidence Ledger.

## 5. Loop 3: Requirement Coverage

Implement deterministic first pass:

- Count requested number of companies/entities when explicit.
- Check required fields from canonical research prompt.
- Check final Artifact exists.
- Check source link presence when required.

Add model-assisted requirement extraction only after deterministic case passes.

Tests:

- Canonical prompt extracts four requirements.
- Missing source creates `missing_requirement` or `missing_source`.
- Three-company requirement fails when final Product has two.

Acceptance:

- Requirement coverage table can be rendered from report JSON.

## 6. Loop 4: Claim Extraction And Evidence Matching

Implement:

- Claim extractor prompt returning JSON.
- Evidence matcher prompt returning JSON.
- Entity presence heuristic.
- Support levels: strong, weak, none, contradicted, not_evaluable.

Tests:

- Supported claim references best evidence id.
- Unsupported claim creates issue.
- Entity absent from evidence creates hallucinated entity issue.
- Weak support creates medium issue.

Acceptance:

- The controlled failure demo flags fake company and unsupported claim.

## 7. Loop 5: Tool Failure And Risk Checks

Implement deterministic checks:

- Failed search/tool events.
- Final Product claims sourced success after failure without retry.
- External action language such as "I sent the email" or "Email these companies now".

Tests:

- Failed search followed by sourced final answer creates `tool_failure_ignored`.
- Failed search followed by explicit limitation does not create high issue.
- Sending email claim creates `unsafe_action`.

Acceptance:

- Demo can intentionally inject one failed tool event and see it in report.

## 8. Loop 6: Score Calculator And Report Writer

Implement:

- Weighted score.
- Status bands.
- caps for critical/unsafe issues.
- report Artifact creation.
- `RELIABILITY_REPORTED` event.

Tests:

- Issue weights subtract expected score.
- Critical issue caps status.
- Unsafe action returns unsafe status.
- Report Artifact is immutable.
- Multiple report versions do not overwrite.

Acceptance:

- `GET /api/work/missions/{missionId}` returns report Artifact and report event.

## 9. Loop 7: API Route

Add route:

```http
POST /api/work/missions/{missionId}/evaluate
```

Request:

```json
{
  "profile": "research_reliability_v1",
  "mode": "live|replay"
}
```

Response:

- Mission detail with latest report.

Tests:

- Requires auth.
- Rejects unowned Mission.
- Evaluates completed Mission.
- Can evaluate replay demo Mission.

Acceptance:

- HTTP smoke creates a report from seeded trace.

## 10. Loop 8: Frontend Reliability Panel

Files:

- `frontend/src/features/work/components/ReliabilityPanel.jsx`
- update `WorkPage.jsx`
- update `InspectorPanel.jsx`
- update `ProgressTimeline.jsx`
- update `eventDisplay.js`
- update CSS.

Implement:

- Score card.
- status label.
- issue badges.
- top issues.
- requirement table.
- claim table.
- suggested fixes.
- limitations.

Tests/smoke:

- Browser shows score and issues.
- Mobile has no horizontal overflow.
- Diagnostics remains collapsed.

Acceptance:

- Demo report is understandable without opening raw JSON.

## 11. Loop 9: Controlled Demo Data

Add deterministic seed/replay:

- successful research case.
- controlled failure case.

Could be:

- script under `scripts/`.
- backend test fixture.
- fake search provider response.

Acceptance:

- Demo does not fail when external search API is unavailable.
- Live path and replay path use same report schema.

## 12. Loop 10: Live Research Path

Depends on Work Mode `web_search`.

Implement:

- `web_search` events feed Evidence Ledger.
- Research Mission prompt encourages Lead to use search.
- final Product references source URLs.

Acceptance:

- Lead can search, produce Product, finish, then evaluator reports against live search observations.

## 13. Loop 11: V1 Contract Closure

Implement the document-to-code closure from `issues/issue8-v1-compliance-closure.md`.

Required implementation:

- Pass `mode` from the API route to Evaluator Runtime.
- Support deterministic `replay` mode without mutating fake search events into the Mission trace.
- Emit `EVALUATION_STARTED`, `RELIABILITY_REPORTED`, and `EVALUATION_FAILED`.
- Add `toolFailures` to the report schema and UI.
- Count issues by severity and by type.
- Include source-backed Research Artifacts in Evidence Ledger.
- Render requirement evidence, claim best source/reason, and tool failure summary in the Reliability Panel.

Tests:

- `mode="replay"` creates a normal report with replay fixture evidence.
- A source-backed Research Artifact becomes Evidence Ledger input.
- Failed tool events appear in `toolFailures`.
- `issueCounts` includes `high` and `type:<issue_type>` entries.
- Evaluator emits lifecycle events and repeated Evaluate stays idempotent.
- Frontend build passes with the expanded report payload.

Acceptance:

- The V1.0 docs and implementation no longer disagree on any public API, report field, state/event, or UI surface.

## 14. Release Gate

V1.0 release passes when:

- Backend tests pass.
- HTTP smoke passes.
- Frontend build passes.
- Browser smoke passes desktop and mobile.
- Successful demo scores ship-ready or minor-review.
- Failure demo catches hallucinated entity, missing source, ignored tool failure, and unsupported claim.
- Report limitations are visible.

## 14. Promotion Notes

Before public promotion:

- Do not remove existing Work Mode APIs.
- Do not alter existing Product reader behavior.
- Keep replay demo separate from live production data.
- Update `api.md` only after route and response shapes are verified.
