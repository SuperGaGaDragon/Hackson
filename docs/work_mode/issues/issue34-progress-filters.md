## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 34: Progress Filters

## Problem

Mission Progress is the process audit trail, but long Missions can produce too many events for a user to scan. When every `Thinking`, tool action, Product update, Delegate window, Search, Reliability report, and warning appears in one uninterrupted feed, users cannot quickly answer focused questions:

- What did the model think or try?
- Which Product events changed output?
- Where are Reliability/Evaluator results?
- Which Delegate or Discussion windows happened?
- What failed or needs attention?

This becomes worse after compact row rules because the feed is calmer but still dense.

## Product Goal

Add Progress filters that let users narrow the visible audit trail without losing the canonical event log.

Default filter:

- `All`

Required filters:

- `Thinking`: model turn start, heartbeat, completed, retrying, invalid turns, and tool decisions.
- `Reliability`: evaluation started, reliability reported, and evaluation failed.
- `Products`: product updated, inspected, and reviewed.
- `Windows`: delegate and discussion window lifecycle events.
- `Search`: web search completed and failed.
- `Inputs`: user input requested, received, follow-up requested, and user instructions.
- `Issues`: failed, blocked, paused retryable, invalid turn, retry, and warnings.

## Self-Grilled Decisions

### 1. Should filters remove events from the backend query?

No for V1.0.x.

Filtering in the client is simpler and preserves the current event API. The full event list remains available for Diagnostics and for switching filters instantly.

Decision:

- Frontend filters the current `events` array.
- Backend API remains unchanged.
- A future server-side query filter can be added only when event volume exceeds client comfort.

### 2. Should multiple filters be selectable at once?

No for the first implementation.

Multiple selection adds visual complexity and unclear counts. The user asked for focused filters like all Thinking or all Reliability.

Decision:

- Use single-select segmented controls.
- Show counts per filter so users know where important events live.

### 3. Where should the filter UI live?

Inside the Progress card header.

Filters belong to the audit trail surface, not the global Mission Header or left rail. They should not compete with Composer or Product reader.

Decision:

- Progress header renders title, total count, and compact filter chips.
- On mobile, chips wrap below the title.

### 4. Should filtered-out events vanish permanently?

No.

The UI must make it clear that the user is viewing a filtered subset and can return to `All`.

Decision:

- `All` stays first.
- Empty filtered states say `No matching events`, not `No events`.
- Diagnostics remains unaffected by Progress filters.

### 5. How does this interact with long-text compacting?

Filters solve navigation; compact rows solve density.

Decision:

- Even filtered rows must follow the two-line default rule from `issue33`.
- Expanded details remain available after filtering.

## Event Group Mapping

`Thinking`:

- `MODEL_TURN_STARTED`
- `MODEL_TURN_HEARTBEAT`
- `MODEL_TURN_COMPLETED`
- `MODEL_TURN_RETRYING`
- `MODEL_TURN_INVALID`
- `TOOL_CALLED`

`Reliability`:

- `EVALUATION_STARTED`
- `RELIABILITY_REPORTED`
- `EVALUATION_FAILED`

`Products`:

- `PRODUCT_UPDATED`
- `PRODUCT_INSPECTED`
- `PRODUCT_REVIEWED`

`Windows`:

- `WORK_WINDOW_OPENED`
- `WORK_WINDOW_COMPLETED`
- `WORK_WINDOW_BLOCKED`
- `WORK_WINDOW_FAILED`
- `DISCUSSION_WINDOW_OPENED`
- `DISCUSSION_WINDOW_COMPLETED`
- `DISCUSSION_WINDOW_BLOCKED`
- `DISCUSSION_WINDOW_FAILED`

`Search`:

- `WEB_SEARCH_COMPLETED`
- `WEB_SEARCH_FAILED`

`Inputs`:

- `USER_INPUT_REQUESTED`
- `USER_INPUT_RECEIVED`
- `USER_FOLLOWUP_REQUESTED`
- `USER_INSTRUCTION_ADDED`

`Issues`:

- `MODEL_TURN_RETRYING`
- `MODEL_TURN_INVALID`
- `WEB_SEARCH_FAILED`
- `EVALUATION_FAILED`
- `WORK_WINDOW_BLOCKED`
- `WORK_WINDOW_FAILED`
- `DISCUSSION_WINDOW_BLOCKED`
- `DISCUSSION_WINDOW_FAILED`
- `MISSION_PAUSED_RETRYABLE`
- `MISSION_BLOCKED`
- `MISSION_FAILED`
- `WARNING`

## Acceptance

- Progress card shows filter chips with counts.
- `All` is selected by default.
- Selecting `Thinking` shows only model/tool decision events.
- Selecting `Reliability` shows evaluator lifecycle and report events.
- Selecting `Products` shows Product/Review/Inspect events.
- Selecting `Issues` surfaces failures, invalid turns, retry, blocked, and warning events.
- Empty filtered state says `No matching events`.
- Expanded row state resets when the filter changes.
- Diagnostics continues to show all events.
- Frontend build and browser smoke pass.
