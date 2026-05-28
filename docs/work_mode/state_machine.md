## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Work Mode State Machine

## 1. Purpose

This document defines Mission, Run, Work Window, Product, and Artifact states for V1.0.

The state machine separates model intent, user action, provider failures, and system failures.

## 2. Mission Status

V1.0 Mission statuses:

```text
draft
running
waiting_input
paused_retryable
stopping
stopped
blocked
failed
completed
```

## 3. Mission Status Meaning

`draft`:

- Mission exists but no active Run has started.

`running`:

- MissionLoopRunner can take model turns.

`waiting_input`:

- The model called `ask_user`.
- UI must show a question.
- User answer may auto-resume V1.0 text-only Missions.

`paused_retryable`:

- Provider timeout, rate limit, or transient runtime failure.
- Progress is preserved.
- User can Resume.

`stopping`:

- User requested Stop.
- Runner should observe and end gracefully.

`stopped`:

- User stop completed.

`blocked`:

- Lead called `block_mission` or budget policy blocked continuation.
- Requires user change, new input, or manual resume policy.

`failed`:

- Runtime/system failure or repeated invalid model turns.

`completed`:

- `finish_mission` validated final Product references and completed the Mission.

## 4. Allowed Mission Transitions

```text
draft -> running
running -> waiting_input
waiting_input -> running
running -> paused_retryable
paused_retryable -> running
running -> stopping
stopping -> stopped
running -> blocked
running -> failed
running -> completed
waiting_input -> stopping
paused_retryable -> stopping
blocked -> running
failed -> running
stopped -> running
completed -> running
```

Restarting terminal Missions is allowed only as a new Run attempt. The previous Run, Events, Products, and Artifacts MUST remain persisted.

## 5. Terminal Status Rules

Terminal for current Run:

- `stopped`
- `blocked`
- `failed`
- `completed`

Terminal for product success:

- only `completed`

User stop:

- MUST produce `stopped`, not `failed`.

Model intentional block:

- MUST produce `blocked`, not `failed`.

Provider transient failure:

- SHOULD produce `paused_retryable`, not `failed`.

Repeated invalid model turns:

- MUST produce `failed`.

## 6. Run Status

Run statuses:

```text
running
paused_retryable
stopped
blocked
failed
completed
```

Each Run belongs to one Mission.

The active Run is the latest non-terminal Run for that Mission.

## 7. Work Window Status

Work Window statuses:

```text
queued
running
completed
blocked
failed
cancelled
```

V1.0 rules:

- Each `delegate_agent` call creates one Work Window.
- Only one Work Window may run at a time per Mission.
- Work Windows run sequentially.
- Work Windows cannot finish the Mission.
- Work Windows cannot open child windows.
- V1.0.3 Discussion Windows use the same lifecycle statuses with `windowType=discussion`.
- UI MUST distinguish delegate Work Windows from Discussion Windows by type and copy, not by a separate hidden state machine.

## 8. Product Status

Product statuses:

```text
active
final_candidate
final
archived
```

Rules:

- A Product starts as `active`.
- `work_product` with `operation=finalize_product` MAY mark a Product `final_candidate`.
- `finish_mission` marks referenced final Products as `final`.
- Prior Products MUST NOT be deleted during a Run.

## 9. Artifact Rules

Artifacts are immutable.

Artifact fields SHOULD include:

- id
- mission id
- product id
- run id
- work window id when applicable
- source agent id
- kind
- title
- content
- summary
- source artifact ids
- review artifact ids when applicable
- discussion artifact ids when applicable
- change summary when applicable
- created at

Rules:

- Artifacts MUST NOT be overwritten.
- Revisions create new Artifacts referencing source Artifact ids.
- Delegate outputs MUST persist as Artifacts.
- Review tools MUST persist Review Artifacts and MUST NOT mutate Product content.
- Discussion tools MUST persist Discussion Artifacts and MUST NOT mutate Product content.
- Web Search tools MAY persist Research Artifacts and MUST NOT mutate Product content.

## 10. Event Types

V1.0 event types:

```text
MISSION_CREATED
MISSION_STARTED
MISSION_PLAN_UPDATED
MODEL_TURN_STARTED
MODEL_TURN_HEARTBEAT
MODEL_TURN_COMPLETED
MODEL_TURN_RETRYING
MODEL_TURN_INVALID
TOOL_CALLED
PRODUCT_UPDATED
PRODUCT_INSPECTED
PRODUCT_REVIEWED
WORK_WINDOW_OPENED
WORK_WINDOW_COMPLETED
WORK_WINDOW_BLOCKED
WORK_WINDOW_FAILED
DISCUSSION_WINDOW_OPENED
DISCUSSION_WINDOW_COMPLETED
DISCUSSION_WINDOW_BLOCKED
DISCUSSION_WINDOW_FAILED
WEB_SEARCH_COMPLETED
WEB_SEARCH_FAILED
USER_INPUT_REQUESTED
USER_INPUT_RECEIVED
MISSION_PAUSED_RETRYABLE
MISSION_STOP_REQUESTED
MISSION_STOPPED
MISSION_BLOCKED
MISSION_FAILED
MISSION_COMPLETED
```

Events MUST be sequenced per Mission.

Large events MUST be collapsed by default in UI.

`WEB_SEARCH_COMPLETED` and `WEB_SEARCH_FAILED` are events, not Mission statuses. Search failure SHOULD return a tool observation and let the Lead choose a next tool when possible. Provider-level outages MAY become `paused_retryable` only when the runtime cannot safely continue.

## 11. Resume Semantics

Resume from `paused_retryable`:

- MUST keep existing Products and Artifacts.
- MUST use the last successful tool observation as part of context.
- MUST NOT replay already persisted tools.

Retryable provider failures:

- MAY emit `MODEL_TURN_RETRYING` before Mission pause when automatic retry budget remains.
- MUST emit `MISSION_PAUSED_RETRYABLE` after automatic retry budget is exhausted.
- MUST keep already persisted lifecycle events and Work Windows.

Process restart recovery:

- On backend startup, a stale `running` Mission from the previous process MUST become `paused_retryable`, not stay `running`.
- Any `running` Work Window owned by that Mission MUST become `failed` with a restart/interruption summary.
- Recovery MUST emit visible events, normally `WORK_WINDOW_FAILED` followed by `MISSION_PAUSED_RETRYABLE`.
- A stale `stopping` Mission MUST become `stopped`.
- Recovery MUST preserve existing Products, Artifacts, Work Windows, and Events so the user can resume.

Resume from `waiting_input`:

- MUST add `USER_INPUT_RECEIVED`.
- MAY auto-resume in V1.0 text-only mode.

Restart from `failed`, `blocked`, `stopped`, or `completed`:

- MUST create a new Run.
- MUST preserve old Run history.

## 12. Budget Exhaustion

If max model turns, max windows, max Products, or max Artifacts is exceeded:

- If a valid final Product exists, backend MAY ask model for `finish_mission` once.
- If no final Product exists, backend SHOULD mark Mission `blocked` with budget reason.

Budget exhaustion MUST NOT silently complete a Mission.

## 13. 代办

- Add concrete MongoDB fields during implementation.
