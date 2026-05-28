## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet State Mapping

## 1. Purpose

This document maps Work Mode persisted state into Desktop Pet behavior.

The mapping must be deterministic. The pet should never infer hidden model intent.

## 2. Inputs

Primary inputs:

- Auto-scan active Mission candidates.
- Mission status.
- Latest relevant event.
- Active Work Window status.
- Product and Artifact availability.
- Polling freshness.

Relevant API responses:

- `GET /api/work/missions/{missionId}`
- `GET /api/work/missions/{missionId}/events?afterSequence=<n>`

Active Mission scan rules:

- Scan all Projects after login and periodically while authenticated.
- Consider only `running`, `waiting_input`, `paused_retryable`, `blocked`, and `stopping` as active.
- Rank active Missions by status priority first, then recency.
- A higher-priority Mission discovered later must replace the currently watched Mission. Example: a `running` Mission replaces an older watched `paused_retryable` Mission even if the paused Mission updated more recently.

## 3. State Priority

When multiple inputs exist, choose the first matching state:

1. `offline`: API/auth/network unavailable.
2. `noActiveWork`: authenticated, scan succeeded, and there are no active Missions.
3. `failed`: Mission status is `failed` or latest event is `MISSION_FAILED`.
4. `done`: Mission status is `completed` or latest event is `MISSION_COMPLETED`.
5. `waiting`: Mission status is `waiting_input` or latest event is `USER_INPUT_REQUESTED`.
6. `paused`: Mission status is `paused_retryable`, `blocked`, `stopped`, or latest event is `MISSION_PAUSED_RETRYABLE` or `MISSION_BLOCKED`.
7. `retrying`: latest event is `MODEL_TURN_RETRYING`.
8. `delegating`: latest active Work Window is `running` or latest event is `WORK_WINDOW_OPENED`.
9. `reviewing`: latest event is `PRODUCT_INSPECTED` or `PRODUCT_REVIEWED`.
10. `writing`: latest event is `PRODUCT_UPDATED` or latest tool is `work_product`.
11. `thinking`: latest event is `MODEL_TURN_STARTED`.
12. `working`: latest event is `MODEL_TURN_HEARTBEAT`, `MODEL_TURN_COMPLETED`, or `TOOL_CALLED`.
13. `idle`: selected Mission exists but has no active signal yet.

## 4. Event Mapping

| Work Mode signal | Pet state | User meaning | Notification |
| --- | --- | --- | --- |
| no active Mission | `noActiveWork` | No Work Mode Mission is currently active | No |
| `draft` | `idle` | Mission is ready but not running | No |
| `MODEL_TURN_STARTED` | `thinking` | Lead is deciding next action | No |
| `MODEL_TURN_HEARTBEAT` | `working` | Long model turn is still alive | No |
| `MODEL_TURN_COMPLETED` | `working` | Lead selected a tool | No |
| `TOOL_CALLED` | `working` | Backend is applying a validated action | No |
| `WORK_WINDOW_OPENED` | `delegating` | Delegate is working | No |
| Work Window `running` | `delegating` | Delegate window is active | No |
| `PRODUCT_UPDATED` | `writing` | Product or Artifact changed | Optional quiet badge |
| `PRODUCT_INSPECTED` | `reviewing` | Lead inspected prior work | No |
| `PRODUCT_REVIEWED` | `reviewing` | Lead reviewed product quality | Optional quiet badge |
| `MODEL_TURN_RETRYING` | `retrying` | Runtime hit a retryable issue | No unless repeated |
| `USER_INPUT_REQUESTED` | `waiting` | User decision needed | Yes |
| `MISSION_PAUSED_RETRYABLE` | `paused` | Mission can be resumed or retried | Yes |
| `MISSION_BLOCKED` | `paused` | Mission intentionally blocked | Yes |
| `MISSION_COMPLETED` | `done` | Mission is complete | Yes |
| `MISSION_FAILED` | `failed` | Mission failed | Yes |

## 5. Visual Behavior

V1 visual states:

- `idle`: still pose.
- `thinking`: slow pulse.
- `working`: small looped work motion.
- `delegating`: pet points outward or shows second worker indicator.
- `writing`: paper or product badge motion.
- `reviewing`: inspect or check motion.
- `retrying`: cautious loop.
- `waiting`: attention pose.
- `paused`: seated or dimmed pose.
- `done`: short completion motion then calm badge.
- `failed`: alert pose without panic animation.
- `offline`: greyed or disconnected pose.

Animation must stay calm. Work Mode is a productivity product, not a toy-only surface.

## 6. Text Policy

Default pet window text should be minimal:

- `No active work`
- `Thinking`
- `Working`
- `Delegate`
- `Writing`
- `Review`
- `Waiting`
- `Paused`
- `Done`
- `Failed`
- `Offline`

Long detail belongs in the popover or web Work Console.

## 7. Notification Policy

Notify only when one of these transitions happens:

- any state -> `waiting`
- any state -> `paused`
- any state -> `done`
- any state -> `failed`

Do not notify repeatedly for the same Mission state unless a new event sequence creates a new action-worthy state.

## 8. Staleness Policy

If polling succeeds but no new events arrive:

- Keep current state.
- Show stale marker only after 90 seconds while Mission is `running`.
- After 5 minutes with no events on a running Mission, show `working` plus stale detail in popover.

Do not mark stale if the Mission is terminal.
