## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 7: Long Model Turn Progress And Timeout UX

## Problem

The public Work Mode smoke can preserve progress when Codex CLI times out, but a normal long writing Mission can still look stalled and then move directly to `paused_retryable`.

That is not a product-level experience for long-form work. The user should be able to see that the Lead Agent is selecting the next tool, that a tool was chosen, that a Delegate window is running, and that a retry is happening before the Mission finally asks for manual resume.

## Current Completion Gap

`docs/work_mode/final_version.md` is not fully complete in the deployed public runtime.

Verified:

- V1.0 JSON Action protocol exists.
- Products, Artifacts, Work Windows, and fixed React UI surfaces exist.
- Deterministic in-process, HTTP, and browser smokes exist.
- Provider timeout preserves progress as `paused_retryable`.

Not yet product-complete:

- The public runtime still uses `codex_cli`; V1.0 target runtime should be the normal API model runtime.
- The true public Codex-backed 8000 CJK character smoke has not completed.
- Lead model turns do not emit visible lifecycle events before the final tool action is available.
- Long provider calls do not emit heartbeat progress while the process is still alive.
- Retryable provider errors pause immediately instead of first using a bounded automatic retry policy.

## Decision

V1.0 MUST add a non-streaming runtime progress layer before V1.2 streaming.

This layer does not stream raw model tokens and does not expose hidden reasoning. It persists safe lifecycle events through the existing polling API.

Required event lifecycle:

```text
MODEL_TURN_STARTED
MODEL_TURN_HEARTBEAT
MODEL_TURN_COMPLETED
TOOL_CALLED
MODEL_TURN_RETRYING
MISSION_PAUSED_RETRYABLE
```

Delegate timeouts after `WORK_WINDOW_OPENED` MUST mark the Work Window `failed` and emit `WORK_WINDOW_FAILED` before the Mission retry or pause path is taken.

## Product Rules

- Timeout MUST remain finite in production.
- Removing timeout is not allowed as a product fix.
- A retryable provider error MAY be retried automatically a bounded number of times.
- After bounded retries are exhausted, the Mission MUST become `paused_retryable`.
- `paused_retryable` MUST keep Products, Artifacts, Work Windows, and Events.
- UI MUST show a compact current activity surface, not only the final timeline.
- Large text still belongs in Product and Artifact surfaces, not progress events.

## Why This Does Not Replace Streaming

This issue gives users Codex-like awareness through persisted lifecycle events.

It still does not provide token-level partial output. V1.2 streaming can later add safe partial artifact/progress streaming without changing the tool protocol.

## Acceptance

- A Lead turn emits `MODEL_TURN_STARTED` before calling the model.
- A validated tool emits `MODEL_TURN_COMPLETED` and `TOOL_CALLED` before execution.
- Slow turns can emit `MODEL_TURN_HEARTBEAT` while still running.
- First retryable provider failure emits `MODEL_TURN_RETRYING` when an automatic retry remains.
- Retry exhaustion emits `MISSION_PAUSED_RETRYABLE`.
- Delegate provider timeout after opening a window marks that window `failed`.
- React Work UI shows the latest activity in a compact, always-visible surface.
- Existing full V1.0 deterministic smoke still passes.
