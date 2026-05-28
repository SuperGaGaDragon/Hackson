## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 6: Idle Interruption Queue

## Self Grill

Question: Should the user be blocked while Idle is generating?

Recommended answer: No. Blocking input makes Idle feel like a machine turn, not a living conversation. The user must be able to type at any time.

Question: Should a user interjection cancel the in-flight model call?

Recommended answer: Not in this implementation slice. Provider cancellation is unreliable across runtimes, and a partial cancel path risks orphaned context packages. Queue the interjection in the UI, let the in-flight turn finish, then immediately send the queued user line as the next product turn.

Question: Does queueing create duplicate or out-of-order messages?

Recommended answer: It can, unless there are two defenses:

- The UI must preserve the queued user line as a pending visible item.
- The backend must protect `Idle Say` with the same per-transcript lock used by `Idle Tick`.

Question: What happens if two tabs send an interjection during the same transcript?

Recommended answer: One turn may run. The other receives stable `423 idle_turn_locked` and the UI keeps the user's draft or shows a retryable failure.

Question: Should the completed Agent message generated before the interjection be hidden?

Recommended answer: No. It was generated from the transcript that existed when it started. The queued user interjection follows immediately, so the next Agent turn responds to the user. Hiding successful turns creates audit gaps.

## Decision

Idle composer must accept user input while an Idle turn is generating.

Runtime policy:

- Current model turn may finish.
- User input during `generating` is queued as a pending interjection.
- As soon as the current turn settles, the queued interjection is sent through `Idle Say`.
- `Idle Say` acquires a per-transcript lock before building context.
- `Idle Say` uses an idempotency key so retries do not duplicate user/Agent pairs.

## Risk

If only the frontend changes, multi-tab input and retries can still corrupt the transcript. If only the backend changes, the product still feels frozen. Both are required.

## Required Tests

- Idle composer remains enabled while `busy=true`.
- Sending during `busy=true` creates a pending queued user item.
- After the in-flight tick completes, the queued user line is sent automatically.
- Backend blocks simultaneous Idle Say or Tick on the same transcript with `423 idle_turn_locked`.
- Same Idle Say idempotency key returns the same saved user/Agent pair after success.

## Non-Goals

- Provider cancellation.
- Streaming token interruption.
- Editing or deleting the in-flight Agent reply.

## Exit Criteria

The user can type during generation, and the next turn safely prioritizes that interjection without duplicate transcript writes.
