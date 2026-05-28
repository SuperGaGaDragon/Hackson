## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 26: Latest Event Window

## Problem

Long public Missions can exceed 100 Progress events.

`get_mission_detail` originally asked the repository for 100 events with no cursor. Mongo returned the earliest 100 events because the repository sorted ascending by `sequence`. That means detail consumers could miss the newest `MISSION_PAUSED_RETRYABLE`, `MISSION_COMPLETED`, `RELIABILITY_REPORTED`, or failure events.

This directly affects Evaluator Runtime:

- It may miss the latest report event and create duplicate reports.
- It may miss recent search failures or completion events.
- The UI detail payload can disagree with the event polling endpoint that sees later events.

## Decision

Mission detail MUST return the latest bounded event window in chronological order.

Repository semantics:

- `after_sequence is not None`: return events after the cursor ascending for polling.
- `after_sequence is None`: return the latest `limit` events, then sort them ascending before returning.

The UI and model context still receive chronological events. The only change is which bounded window is selected.

## Consequences

- Long Missions show the latest Progress state in detail payloads.
- Evaluator Runtime can see the latest current-version `RELIABILITY_REPORTED` event for idempotency.
- Model context sees recent work instead of stale early setup events.

## Acceptance

- A Mission with more than 100 events returns the last 100 events from `get_mission_detail`.
- Returned events are still sorted ascending by sequence.
- Cursor-based event polling behavior remains unchanged.
- Work Mode full tests and public smokes pass.
