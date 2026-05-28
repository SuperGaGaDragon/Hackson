## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 24: Empty Model Output Should Pause Retryably

## Problem

Public logging showed a Work Mission failing with `model_response_missing_text` while a Delegate window was drafting a long chapter.

The service had no traceback and no 5xx. The model runtime returned through the normal structured error boundary, but Work Mode treated the empty output as a non-retryable tool execution failure and marked the whole Mission `failed`.

For long-running Codex CLI backed work, empty output can happen when the provider process exits without a readable output artifact, especially around restarts, cancellation, or provider-side transient behavior. Product-wise this should not destroy a long Mission run.

## Decision

`model_response_missing_text` MUST be retryable in Work Mode model-call adapters.

Expected behavior:

- Lead turn empty output may retry within the configured retry budget.
- If retry budget is exhausted, Mission becomes `paused_retryable`.
- Delegate/discussion empty output marks the active Work Window `failed` with the error code, then pauses the Mission retryably.
- User can resume with `Start`.

## Non-Goals

- Do not fabricate delegate content when the model returns empty output.
- Do not silently skip the failed window.
- Do not auto-resume after process restart in V1.0.x.

## Acceptance

- `DelegateResultClient` maps `model_response_missing_text` to `ToolActionClientError(..., retryable=True)`.
- Work Mode loop pauses retryably for delegate empty output.
- Existing timeout/rate-limit retry behavior is unchanged.
- Target-machine Work Mode tests pass before deployment.
