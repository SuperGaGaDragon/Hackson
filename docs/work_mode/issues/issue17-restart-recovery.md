## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 17: Restart Recovery For Running Work Missions

## Problem
Public testing exposed a production failure mode on `8145`.

When a Work Mission is running a long Codex-backed turn, FastAPI `BackgroundTasks` keeps the request-owned background function inside the uvicorn process. During systemd restart, uvicorn waits for that task. If the task is blocked in a model subprocess, the service enters `deactivating`, Cloudflare sees origin connection refused, and the Mission can remain stuck as `running` with an open Work Window.

Observed public Mission:

- Mission: `6a17e0d8a86e4f0e354d1974`
- Last persisted state before interruption: `WORK_WINDOW_OPENED`
- Service state during bug: `deactivating (stop-sigterm)`
- Child process: `codex exec`
- User-visible result: polling continues, but Mission remains running without new progress.

## Decision
V1.0.x must not rely on FastAPI `BackgroundTasks` for long Work Mission execution.

Immediate fix:

- Start Work Mission execution through a process-local daemon worker launcher, not request-owned `BackgroundTasks`.
- On application startup, recover interrupted Work state:
  - `running` Mission -> `paused_retryable`
  - `stopping` Mission -> `stopped`
  - `running` Work Window -> `failed`
  - Emit visible recovery events so the UI can explain what happened.
- Keep all Products, Artifacts, Events, and Work Windows.
- Let the user resume from `paused_retryable` with `Start`.

This is not a durable worker queue. It is the minimum recovery layer that prevents silent stuck state and protects public restart behavior.

## Non-Goals
- Do not add Redis, Celery, or a separate queue service in this patch.
- Do not auto-resume interrupted Missions on startup.
- Do not hide the interruption from users.
- Do not mark interrupted work as completed.

## Acceptance
- A Mission interrupted after `WORK_WINDOW_OPENED` is no longer permanently `running`.
- Startup recovery emits `WORK_WINDOW_FAILED` and `MISSION_PAUSED_RETRYABLE`.
- `/start` can resume the recovered Mission.
- systemd restart is not blocked by request-owned FastAPI background work.
- Public health recovers quickly after restart.

## Follow-Up
V1.1 should replace process-local daemon workers with a durable queue and explicit worker lease records. Startup recovery should then use leases instead of inferring from Mission state alone.
