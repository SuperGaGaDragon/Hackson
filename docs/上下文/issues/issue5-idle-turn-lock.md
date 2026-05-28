## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 5: Idle Turn Lock And Idempotency

## Decision

Idle Tick needs a server-side turn lock before Background Idle can ship.

The first implementation protects one conversation transcript version at a time:

- lock key: `user_id`, `conversation_id`, and current `message_count`.
- lock holder: request idempotency key when provided, otherwise a generated request id.
- lock lifetime: short TTL suitable for one model turn.
- duplicate same idempotency key returns the completed result when available.
- duplicate different key for the same transcript returns stable `idle_turn_locked`.

## Risk

Without this lock, two tabs, retries, browser timers, or future background runners can generate two next-Agent messages from the same transcript. That corrupts speaker alternation, creates duplicate costs, and makes context package audit misleading.

## Constraints

- Locking must happen before context build and model generation.
- Context Package persistence must remain on successful lock acquisition.
- Failed model generation must release the lock or mark it failed so a later tick can retry.
- Same idempotency key should not create a second Agent message after success.
- The lock is not a scheduler and does not enable browser-closed Background Idle.
- Background Idle remains blocked until this exists.

## Required Tests

- Two simultaneous ticks for the same conversation/message count cannot both generate.
- Retrying with the same idempotency key after success returns the same Agent message/context response.
- Retrying with a different key while a turn is running returns `423 idle_turn_locked`.
- Provider failure releases or fails the lock and does not save an Agent reply.
- A later tick after failure can run.

## 代办

- Decide whether V1.1 stores completed response snapshots in Mongo or only completed assistant message ids.
