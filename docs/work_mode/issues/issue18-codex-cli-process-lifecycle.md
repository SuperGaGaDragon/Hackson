## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 18: Codex CLI Process Lifecycle

## Problem
Public Work testing exposed a process lifecycle bug on `8145`.

Mission `6a1833decf117568867bd0f3` kept progressing, but an earlier `codex exec` process group remained alive after the Mission had already persisted `MODEL_TURN_INVALID` and moved to later turns. The stale process had a zero-byte output file and stayed under the uvicorn service cgroup.

This is product-risky because stale Codex processes:

- consume memory and task slots;
- make the UI look slower or less trustworthy;
- can block clean restart if enough accumulate;
- make timeout diagnosis ambiguous because current and stale model calls look identical in `ps`.

## Decision
The Codex CLI provider must own the full lifecycle of every process group it starts.

Required behavior:

- On timeout, send `SIGTERM` to the process group, wait briefly, then send `SIGKILL` if the group does not exit.
- On successful return, still terminate the process group after output has been captured so helper processes do not linger.
- On non-zero return, terminate the process group before raising `model_codex_cli_error`.
- Clean up the temporary output file in all cases.

This is a provider-level fix. It does not change Work Mode tool semantics.

## Non-Goals
- Do not remove production timeouts.
- Do not expose Codex CLI as a model-visible tool.
- Do not replace the process-local Work worker with a durable queue in this patch.

## Acceptance
- Unit tests prove timeout cleanup escalates from `SIGTERM` to `SIGKILL`.
- Unit tests prove successful Codex CLI calls also trigger process-group cleanup.
- Public process checks show no stale zero-output Codex process after a completed or invalid model turn.

## Follow-Up
Durable worker leases should record active model-call ids and process ids. That belongs with the V1.1 worker lease / queue hardening, not this narrow provider cleanup patch.
