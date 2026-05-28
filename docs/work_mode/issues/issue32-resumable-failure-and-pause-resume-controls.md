## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 32: Resumable Failure And Pause/Resume Controls

## Problem

Public Work Mode Missions can preserve useful Products, Artifacts, Windows, and Events, but the current control
semantics make recoverable runner exits look terminal.

Observed public failure cluster:

- `mission_loop_turn_budget_exceeded`
- `discussion_result_invalid`
- `tool_action_schema_invalid`
- repeated `tool_action_schema_invalid`

The model cannot keep working after the runner exits. It can only continue when the user starts a new Run against
the same persisted Mission state. The backend already allows this for `failed`, `paused`, `paused_retryable`,
`stopped`, and `blocked`, but the UI still says `Start` and repeated invalid-turn exhaustion is stored as `failed`.

## Self Grill

Question: Is `Start` already a checkpoint resume?

Decision: Yes, when the Mission is not `draft`. `start_mission` creates a new Run and the Lead context is rebuilt
from persisted Mission detail, including Product manifest, recent Events, Work Windows, Artifacts, and Reliability
reports. It does not replay already persisted tool effects.

Question: Should repeated invalid model turns be `failed`?

Decision: No for model-correctable invalid turns. Repeated schema/tool-contract invalid turns mean the current Run
budget is exhausted, not that the Mission data is corrupt. The product should pause retryably and expose Resume.

Question: Should user Pause be the same as Stop?

Decision: No. Pause is a reversible control request. Stop remains a backend-compatible hard stop endpoint, but the
main UI should use Pause/Resume. A paused Mission MUST be resumable without losing history.

Question: Should the frontend show Start and Stop at the same time?

Decision: No. The primary action is stateful:

- `draft` -> Start.
- `running` -> Pause.
- `stopping` -> Pausing, disabled.
- `paused`, `paused_retryable`, `failed`, `stopped`, `blocked` -> Resume.
- `waiting_input` -> answer form owns the next action.
- `completed` -> Continue form owns the next action.

## Decision

Introduce a reversible pause path and treat model-correctable exhaustion as resumable:

1. Add `POST /api/work/missions/{missionId}/pause`.
2. Pause a running Mission by marking it `stopping` with `controlRequest.mode=pause`.
3. When the runner observes the request, mark the Mission `paused` and the active Run `paused`.
4. Keep `POST /stop` for compatibility and hard-stop semantics.
5. Convert invalid-turn budget exhaustion and loop-turn budget exhaustion to `paused_retryable`.
6. Keep `failed` for true runtime/system failures where automatic continuation is unsafe.
7. `MISSION_STARTED` after non-draft statuses MUST use `title=Resumed` and include previous status/error metadata.
8. SSE event streams MUST close for non-running pause states so the UI can return to idle controls without hanging.

## Runtime Mapping

```text
draft start -> running
running pause request -> stopping(controlRequest.mode=pause)
stopping pause observed -> paused
paused resume -> running(new Run)
paused_retryable resume -> running(new Run)
failed resume -> running(new Run, compatibility path)
invalid turn under budget -> retry with lastObservation
invalid turn over budget -> paused_retryable
tool contract rejection under budget -> retry with lastObservation
tool contract rejection over budget -> paused_retryable
turn budget exceeded -> paused_retryable
hard system/runtime invariant failure -> failed
```

## UX Contract

- The main control MUST be one stateful button, not Start plus Stop.
- Resume copy MUST appear for `paused`, `paused_retryable`, `failed`, `stopped`, and `blocked`.
- Pause copy MUST appear while a Mission is `running`.
- Pausing copy MUST appear while a Mission is `stopping`.
- Completed Missions MUST keep using the existing Continue form instead of replaying Start.
- Input-request Missions MUST keep using the existing answer form.

## Acceptance

- Service test proves `failed` or `paused_retryable` Start emits a resumed Run with previous-state metadata.
- Service/loop test proves user Pause becomes `paused`, not `stopped`.
- Loop test proves repeated schema/tool contract invalid turns become `paused_retryable`, not `failed`.
- Loop test proves max-turn budget exhaustion becomes `paused_retryable`.
- Route test proves `/pause` records a pause request for a running Mission.
- Frontend build passes with the stateful Start/Pause/Resume control.
- Target-machine public deployment verifies health, root HTML, built assets, and no new traceback/500 in logs.
