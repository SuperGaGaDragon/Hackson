## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 10: Reliability Score Is Not Objective Truth

## Problem

Users may read `Reliability 0 / 100` or `80 / 100` as an absolute, objective grade. That is not what the V1 evaluator
can honestly provide.

The evaluator inspects visible Work Mode trace, Products, Artifacts, and evidence. It can flag unsupported claims,
missing requirements, tool failures, and incomplete Missions. It cannot prove that every claim is true, and it cannot
know facts that are absent from the evidence ledger.

## Self-Grilled Decisions

Question: Is the current score objective?

Decision: No. It is deterministic for a given trace and scoring model, but deterministic does not mean objectively
true. It is a risk score based on visible evidence and rule weights.

Question: Should the score be removed?

Decision: No. The score is useful for triage and product clarity. Removing it would make quality regressions harder to
notice. The fix is to label it accurately and show evidence/limitations beside it.

Question: Should low scores always block completion?

Decision: For research/paper-like Missions, yes when blocking issues remain. But the reason must be visible and tied
to trace-backed issues. For non-research work, the score should not pretend to be universal.

Question: Should no-evidence work score `0 / 100`?

Decision: Not automatically. No evidence is a root-cause limitation and must prevent `ship_ready`, but repeated
unsupported-claim penalties should not create fake precision. `0 / 100` is reserved for catastrophic reports.

## Decision

Reliability UI and report metadata must present score as:

```text
Risk score, not proof.
```

Required report metadata:

- `scoreMeaning`: short user-facing label.
- `confidence`: `high | medium | low`.
- `confidenceReason`: short explanation grounded in evidence ledger and evaluator limitations.
- `objective`: always `false` for V1 profiles.

Confidence rules for V1:

- `low`: no evidence ledger, incomplete Mission, replay-only evidence, or major evaluator limitation.
- `medium`: some evidence exists but unsupported/weak claims or missing requirements remain.
- `high`: strong evidence coverage and no high/critical unresolved issues.

The score remains deterministic and useful, but it must not be framed as objective truth.

## UI Contract

Reliability Panel must show:

- Score.
- Status.
- `Risk score` label.
- Confidence level.
- One-line limitation text.

The panel must not use copy that implies absolute verification, such as:

- `Objective score`
- `Truth score`
- `Guaranteed`
- `Certified correct`

Acceptable labels:

- `Risk score`
- `Trace-backed check`
- `Needs review`
- `Evidence limited`

## Acceptance

- Reliability report payload includes `objective=false`, `scoreMeaning`, `confidence`, and `confidenceReason`.
- Reliability Panel renders confidence and "not proof" language.
- Existing score/history behavior remains unchanged.
- Tests cover no-evidence reports returning low confidence.
- Tests cover source-backed reports not claiming objective truth.
