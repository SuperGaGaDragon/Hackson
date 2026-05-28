## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 21: V1.2 Streaming Execution Spec

## Problem
`issue5-streaming.md` defines the direction for V1.2, but it is not detailed enough for implementation. It does not specify the transport, reconnect behavior, event payload, frontend fallback, or tests.

## Decision
V1.2 streaming uses Server-Sent Events over the existing Mission event log.

Endpoint:

```text
GET /api/work/missions/{missionId}/events/stream?afterSequence=123
```

Why SSE:

- Work Mode progress is server-to-browser only.
- Existing Mission events are already ordered by `sequence`.
- Browser `EventSource` supports reconnect.
- Polling can remain the fallback without a second product model.
- WebSocket complexity is not needed for V1.2.

## Stream Contract
Each SSE message represents one persisted Mission event.

```text
id: <event.sequence>
event: work_event
data: <EventResponse JSON>
```

Heartbeat messages keep long connections alive:

```text
event: ping
data: {"status":"ok"}
```

Rules:

- The stream MUST only emit persisted public events that `/events` can also return.
- The stream MUST NOT emit raw model tokens.
- The stream MUST NOT emit hidden reasoning or chain-of-thought.
- The stream MUST NOT expose provider logs, shell output, or Codex CLI internals.
- `afterSequence` MUST behave like the polling API: only later events are streamed.
- `Last-Event-ID` MAY be accepted as a reconnect cursor when `afterSequence` is absent.
- Terminal Mission statuses MAY close the stream after pending events are flushed.

## Backend Shape
Add a route:

```text
GET /api/work/missions/{missionId}/events/stream
```

Implementation:

- Validate user auth exactly like `/events`.
- Confirm Mission exists before opening the stream.
- Poll repository events internally at a short bounded cadence, initially 1 second.
- Emit only events with `sequence > cursor`.
- Send a `ping` event every 15 seconds when no Mission event is available.
- Stop after terminal status is observed and no new events remain.

This is still event-log streaming, not model-token streaming. It can be implemented without changing the Mission loop or tool protocol.

## Frontend Shape
Add an optional stream client:

- Try `EventSource` for running/stopping Missions.
- Merge streamed events through the same `mergeEvents` path as polling.
- Refresh Mission detail after receiving streamed events so Products, Artifacts, and Work Windows stay current.
- Fall back to existing polling when EventSource is unavailable, errors, or closes unexpectedly.
- Keep polling behavior for browsers/environments where Authorization headers cannot be sent through EventSource until token delivery is explicitly supported.

Important auth constraint:

- Native `EventSource` cannot set custom `Authorization` headers.
- First implementation MUST either use cookie/session-compatible auth, a short-lived stream token, or keep frontend polling while backend SSE is verified through HTTP smoke.
- Do not put long-lived bearer tokens in query strings.

## Acceptance
- Backend route streams existing Mission events in order.
- Backend stream supports `afterSequence`.
- Backend sends `ping` when idle.
- Backend closes after terminal status.
- Polling `/events` still works unchanged.
- Tests cover stream ordering, cursor behavior, ping behavior, and auth isolation.
- Frontend keeps polling fallback until auth-safe stream connection is implemented.

## Non-Goals
- No token-level model streaming.
- No partial JSON tool action streaming.
- No WebSocket.
- No hidden reasoning display.
- No replacement of the persisted event log.

