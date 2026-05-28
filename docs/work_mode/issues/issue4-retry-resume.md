## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
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
- unrecoverable adapter/runtime exception

## Runtime Mapping

```text
invalid turn under retry limit -> retry with format error observation
invalid turn over retry limit -> paused_retryable
rate limit / timeout -> paused_retryable
block_mission -> blocked
user pause -> paused
legacy user stop -> stopped
finish_mission valid -> completed
```

## Resume Rules

- Resume from `paused` and `paused_retryable` MUST continue from persisted state.
- Resume MUST NOT replay already executed tools.
- Resume from `failed`, `blocked`, or `stopped` MUST create a new Run for compatibility and preserve history.
- User answer from `waiting_input` MAY auto-resume in V1.0 text-only mode.

## Acceptance

- Provider timeout creates `paused_retryable`.
- Resume continues and can complete.
- Invalid JSON retries and then pauses retryably after limit.
- User pause never records `failed`.
