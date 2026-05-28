## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 8: V1 Compliance Closure

## Problem

The Evaluator Runtime documents define a full V1.0 contract, but partial implementation can make the product look finished while key contract pieces are missing.

Observed closure gaps:

- `mode=live|replay` exists in the API request but replay is not executed.
- Progress only records `RELIABILITY_REPORTED`; the UI contract also requires `EVALUATION_STARTED` and `EVALUATION_FAILED`.
- Reports include issue counts by severity but not by issue type.
- Reports do not expose a first-class tool failure summary.
- Evidence Ledger is limited to web search events and misses source-backed Research Artifacts.
- Reliability UI does not show requirement evidence, claim reasons, best source, or tool failures clearly enough.

## Decision

V1.0 closure MUST make the implemented contract match the evaluator docs before adding new product scope.

Required changes:

1. `POST /api/work/missions/{missionId}/evaluate` MUST pass `mode` to Evaluator Runtime.
2. `mode="replay"` MUST run through the same report builder and report schema as live mode, using deterministic replay evidence when live trace evidence is missing.
3. Evaluator Runtime MUST emit `EVALUATION_STARTED`, `RELIABILITY_REPORTED`, and `EVALUATION_FAILED` as visible Work events.
4. `ReliabilityReport.issueCounts` MUST include severity counts and type counts.
5. `ReliabilityReport.toolFailures` MUST summarize failed tools with event id, sequence, tool, code, and retryability.
6. Evidence Ledger MUST include `WEB_SEARCH_COMPLETED` results and source-backed Research Artifacts. Final Product prose is still not evidence.
7. Reliability UI MUST render score, status, issue badges, requirement evidence, claim best source/reason, tool failures, limitations, and expanded Progress details without using Diagnostics as the primary surface.

## Self-Grilled Decisions

### Should V1.0 add an open-ended LLM judge now?

No.

The docs require structured evaluator outputs, not a vague opinion prompt. For V1.0 closure, deterministic extractors and matchers must produce the same structured JSON report contract. Model-assisted extraction can replace the deterministic implementation later only if it remains schema-bound and failure-safe.

### Should replay mutate Mission trace by inserting fake search events?

No.

Replay mode should persist a real Reliability Report and report lifecycle events, but deterministic replay evidence is marked with provider `replay_fixture`. It should not pretend that the Lead Agent actually ran live search.

### Should failed evaluations leave a partial report?

Only when report construction can still complete.

If the runtime cannot produce a valid report, it emits `EVALUATION_FAILED` with a stable error code and does not create a fake successful report.

### Should `evaluate_product` revise the Product after finding issues?

No.

It returns a report and a recommended next tool. The Lead must choose `web_search`, `work_product`, `ask_user`, or another Work Mode tool to revise content.

## Consequences

- The evaluator becomes a real product surface instead of a raw diagnostic attachment.
- Replay demos are reliable without hiding that they are replay fixtures.
- Lead-visible `evaluate_product` can support repair loops without mutating Product content.
- Future model-assisted evaluator checks have a stable schema and tests to preserve.

## Acceptance

- Route tests cover `mode="replay"`.
- Unit tests cover source-backed Research Artifact evidence.
- Unit tests cover tool failure summary and issue counts by severity and type.
- Runtime tests cover `EVALUATION_STARTED`, idempotency, and `EVALUATION_FAILED`.
- Frontend build passes after Reliability and Progress UI support the new report fields.
