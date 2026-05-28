## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 6: Incomplete Mission Gate

## Problem

Public testing showed a paused Work Mission could receive a `ship_ready` Reliability Report if it had a final-looking Artifact.

That is wrong product behavior.

Evaluator Runtime is a quality gate for the whole Mission trace, not only a text scorer. A Mission that is `running`, `waiting_input`, `paused_retryable`, `blocked`, `failed`, `stopping`, or `stopped` has not completed the Work Mode contract. Even if it contains usable draft content, the report must tell the user that the Mission is incomplete.

Repeated clicks on Evaluate also created multiple identical Reliability Reports, which made Progress noisy and obscured the real state.

## Decision

V1.0 MUST apply a Mission completion gate:

- `mission.status == completed` is required for `ship_ready`.
- Any other status creates a `mission_incomplete` issue.
- `mission_incomplete` has high severity and caps status at `needs_human_review`.
- Failed or paused Missions can still be evaluated, but the report describes the Product as draft or partial quality, not ready-to-ship quality.

Evaluator Runtime MUST persist versioned reports.

If the latest event is a current-version `RELIABILITY_REPORTED` event and no new Work trace exists after it, Evaluate returns the existing Mission detail without creating another report. If the evaluator version changes, a new report is allowed so old bad reports can be superseded.

## Self-Grilled Decisions

### Should paused_retryable be unsafe_to_ship?

Not by default.

`paused_retryable` often means the model/tool infrastructure stopped after partial work. The Product may be useful for human review, but it is not completed. `needs_human_review` is the right default gate.

### Should the evaluator refuse to run on incomplete Missions?

No.

Running the report is useful because it shows what is missing and why the current output is not ready. Refusing to run would hide the quality signal the user asked for.

### Should repeated Evaluate always rerun?

No.

Repeated clicks without new Work trace should be idempotent. Re-running only matters when new artifacts/events exist or when the evaluator version changes.

## Consequences

- Users do not see `100 / 100 ship_ready` on paused or failed Missions.
- Progress no longer fills with duplicate Reliability events during repeated clicks.
- Old reports can be corrected by bumping the evaluator version.

## Acceptance

- A paused Mission with a final-looking Artifact reports `mission_incomplete`.
- The paused Mission status is capped at `needs_human_review`.
- A completed Mission can still reach `ship_ready` when no issues are found.
- Two Evaluate calls without new trace create only one current-version Reliability Report.
- Existing report schema remains backward-compatible for the UI.
