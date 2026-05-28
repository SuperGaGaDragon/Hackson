## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime State Machine

## 1. Purpose

This document defines Evaluation Run, Reliability Report, Reliability Issue, and Evidence Item states.

Evaluator Runtime state is separate from Mission state. A Mission can be completed while its latest Reliability Report says `needs_human_review`.

## 2. Evaluation Run States

```text
queued
  -> running
  -> completed
  -> failed
  -> cancelled
```

Rules:

- `queued` means evaluation has been requested but no checks have started.
- `running` means trace and evidence are being inspected.
- `completed` means a Reliability Report was produced.
- `failed` means no report could be produced.
- `cancelled` means a newer evaluation superseded the run before completion.

V1.0 MAY skip explicit `queued` and run synchronously for small demo cases, but the public state model should preserve it.

## 3. Reliability Report States

```text
draft
  -> published
  -> superseded
```

Rules:

- `draft` exists only during report assembly.
- `published` reports are visible in the Work Console.
- `superseded` reports remain readable after a newer report is published.
- Reports MUST NOT be overwritten.

## 4. Reliability Status

Reliability status is not the same as report lifecycle.

Allowed values:

- `ship_ready`
- `minor_review`
- `needs_human_review`
- `unsafe_to_ship`

Transition examples:

```text
first report: needs_human_review
Lead revises Product
second report: minor_review
Lead fixes missing source
third report: ship_ready
```

## 5. Reliability Issue States

V1.0 issue lifecycle:

```text
open
  -> resolved
  -> accepted_risk
  -> obsolete
```

V1.0 may derive issue state by comparing report versions instead of storing state transitions.

Rules:

- `open` means the issue appears in the latest report.
- `resolved` means a newer report no longer detects the issue and can link to a fix Artifact.
- `accepted_risk` means a human explicitly accepts the issue in a later version.
- `obsolete` means a newer Product version made the issue irrelevant.

V1.0 UI can show only open issues. V1.5 should show issue history.

## 6. Evidence Item States

Evidence items are immutable once included in a report.

```text
available
  -> referenced
  -> stale
```

Rules:

- `available` means a source item exists in the Evidence Ledger.
- `referenced` means at least one claim or issue points to it.
- `stale` means recency policy says it should no longer be trusted without refresh.

V1.0 may omit stale handling unless the source includes published dates.

## 7. Trigger Policy

V1.0 triggers:

- Manual: user clicks Evaluate.
- Automatic: Research Mission reaches `completed`.
- Demo replay: seeded trace is evaluated immediately.

V1.0 should avoid evaluating every intermediate event by default.

V1.5 triggers:

- Checkpoint after `web_search`.
- Checkpoint before `finish_mission`.
- Checkpoint after revision.

## 8. Failure Handling

If evaluator model calls fail:

- Deterministic checks should still produce a partial report when possible.
- Report status should be at most `needs_human_review`.
- Add `evaluation_limitation` issue with stable error code.

If Evidence Ledger is empty:

- Requirement coverage can still run.
- Claim checks should become `not_evaluable`.
- Report should warn that the Mission lacks trace-backed evidence.

If Mission has no final Product:

- Report should focus on incomplete state.
- Score should not exceed 60.

## 9. Relationship To Mission State

Mission states remain owned by Work Mode.

Evaluator Runtime MAY read:

- `draft`
- `running`
- `waiting_input`
- `paused_retryable`
- `blocked`
- `failed`
- `completed`

Evaluator Runtime MUST NOT directly set Mission state in V1.0.

Later Repair Loop MAY let the Lead Agent consume Reliability Issues and choose Work Mode tools, but the tool decision still belongs to Work Mode.
