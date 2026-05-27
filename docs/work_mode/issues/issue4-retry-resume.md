## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 4: Retry And Resume

## Problem

Model loops fail in different ways. Treating every failure as `failed` destroys useful progress and forces users to restart long Missions.

## Decision

V1.0 MUST distinguish invalid model turns, transient provider failures, model-declared blocks, user stops, and successful completion.

## Failure Categories

Invalid model turn:

- invalid JSON
- plain assistant text
- unknown tool
- schema validation failure

Transient provider failure:

- rate limit
- timeout
- network unavailable

Model-declared block:

- `block_mission`

User stop:

- stop request from UI/API

System failure:

- persistence error
- invariant violation
- exhausted invalid retries

## Runtime Mapping

```text
invalid turn under retry limit -> retry with format error observation
invalid turn over retry limit -> failed
rate limit / timeout -> paused_retryable
block_mission -> blocked
user stop -> stopped
finish_mission valid -> completed
```

## Resume Rules

- Resume from `paused_retryable` MUST continue from persisted state.
- Resume MUST NOT replay already executed tools.
- Resume from terminal statuses MUST create a new Run.
- User answer from `waiting_input` MAY auto-resume in V1.0 text-only mode.

## Acceptance

- Provider timeout creates `paused_retryable`.
- Resume continues and can complete.
- Invalid JSON retries and then fails after limit.
- User stop never records `failed`.
