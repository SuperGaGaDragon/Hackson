## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 9: Latest Report History And Score Calibration

## 1. Problem

Public Work Mode testing showed two confusing Reliability behaviors:

- Repeated `evaluate_product` runs can leave users unsure which Reliability Report is current.
- Long research drafts with no usable Evidence Ledger can score `0 / 100` because many unsupported or hallucinated-entity issues are all charged independently from the same root cause.

Both behaviors are technically explainable but poor product behavior.

## 1.1 Production Evidence

Confirmed on public `8145` before rollout:

- Mission `6a1873a07930f43553a9031a` produced Reliability Report Artifacts `6a1878227930f43553a903b0` and `6a1878b97930f43553a903b4`.
- Events `#129` and `#132` both reported `0 / 100` with distinct `reportArtifactId` values, so the UI must use event sequence and `reportArtifactId` rather than Artifact array order to pick the current report.
- The report text showed a large number of unsupported claims from the same missing Evidence Ledger root cause; this should remain `needs_human_review`, but should not mechanically collapse every long no-evidence draft to `0 / 100`.

## 2. Decision

Reliability UI MUST make the current report unambiguous:

- The primary Reliability card MUST show the latest `RELIABILITY_REPORTED` event by event sequence.
- The latest event's `reportArtifactId` MUST select the matching Reliability Report Artifact when available.
- Older reports MUST remain available as collapsed history.
- History rows MUST show score, status, mode, time, and report id.
- Diagnostics MAY still show raw payloads, but the user should not need Diagnostics to know the current Reliability state.

Evaluator scoring MUST remain strict but root-cause aware:

- Missing evidence MUST still cap status at `needs_human_review`.
- Mission incomplete MUST still prevent ship-ready status.
- Unsupported claim and hallucinated entity penalties MUST be capped so one missing evidence root cause does not mechanically drive every long draft to `0`.
- `0 / 100` remains possible for genuinely catastrophic reports, such as unsafe actions, contradictions, ignored tool failures combined with many independent unresolved issues, or severe missing requirements.

## 3. Constraints

- Do not hide older reports.
- Do not overwrite report Artifacts.
- Do not let UI choose current reports by Artifact array order alone.
- Do not weaken finish gates for research/paper-like Missions.
- Do not report no-evidence research as `minor_review` or `ship_ready`.

## 4. Acceptance

- A Mission with two Reliability Reports shows the second report in the primary card.
- The first report is visible in collapsed history.
- If the latest `RELIABILITY_REPORTED` event references a report Artifact, the UI uses that Artifact payload.
- If event payload and Artifact list are temporarily out of sync, the UI falls back to the newest report Artifact.
- A no-evidence long research draft produces `needs_human_review` but not automatic `0 / 100` purely from repeated unsupported-claim and hallucinated-entity issues.

## 5. Rollout Guard

- Validate score calibration with a deterministic no-evidence long research draft test.
- Validate Reliability history with both event-backed and Artifact-backed reports.
- Do not delete older Reliability Artifacts during migration; history is product state.
