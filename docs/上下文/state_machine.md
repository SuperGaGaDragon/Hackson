## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Context Runtime State Machine

## 1. Purpose

This document defines the product state transitions that affect Context Runtime.

## 2. Conversation Modes

| Mode | Meaning | Context Source |
| --- | --- | --- |
| `idle` | Two Agents talk in the visible world timeline. | idle transcript, topic direction, Agent profiles, idle summaries, account memory, idle relationship memory |
| `companion_1` | User explicitly joins an idle conversation. | child transcript, parent idle transcript, transition context, user profile, account memory |
| `companion_2` | User opens direct companion chat. | companion transcript, user profile, account memory |
| `work` | User starts structured task execution. | Work Mode mission state, tool trace, account memory, work-private memory |

## 3. Idle Turn States

| State | Trigger | Next State |
| --- | --- | --- |
| `idle_ready` | Tick requested and budget allows | `context_building` |
| `context_building` | Context package persisted | `generating` |
| `generating` | Model reply succeeds | `persisting_reply` |
| `persisting_reply` | Message saved and jobs enqueued | `idle_ready` |
| `generating` | Provider rate limit or timeout | `cooldown` |
| `cooldown` | Next eligible time passes | `idle_ready` |
| `generating` | User submits Idle Interruption | `generating_with_queued_interruption` |
| `generating_with_queued_interruption` | Model reply succeeds | `persisting_reply_then_idle_say` |
| `persisting_reply_then_idle_say` | Queued Idle Say starts | `context_building` |

Background Idle:

- Background Idle defaults off.
- If Background Idle is disabled, browser-closed sessions MUST NOT schedule new idle turns.
- If Background Idle is enabled, the server MAY schedule new idle turns only within budget, cooldown, and failure limits.
- Provider failures MUST move the runner to cooldown instead of retrying in a loop.

Collaborative convergence:

- Each generated Idle turn keeps the conversation in `generating`, but the prompt must test whether the previous disagreement still changes action, risk, or decision criteria.
- If no new decision-relevant disagreement remains, the Agent settles the point instead of adding another debate turn.

## 4. Idle Say States

Idle Say is one product turn when the runtime is idle:

```text
user interjection
  -> build context with pending user line
  -> generate Agent reply
  -> save user message
  -> save Agent message
```

If generation fails, the user message MUST NOT be persisted as a half-turn unless the product deliberately introduces draft retry state.

Idle Interruption is queued user intent when the runtime is already generating:

```text
idle generating
  -> user submits interjection
  -> UI shows pending queued user line
  -> current Agent reply finishes or fails
  -> queued Idle Say runs before any Auto tick
```

Backend rule:

- Idle Say MUST acquire the per-transcript idle turn lock before context build.
- A completed Idle Say idempotency key returns the same user/Agent pair.
- A concurrent different key returns `423 idle_turn_locked`.

## 5. Companion 1 States

```text
join request
  -> create child conversation
  -> save user join message
  -> build transition context from parent idle
  -> generate Agent reply
  -> save Agent reply
  -> continue child conversation
```

Follow-up turns use child transcript as direct history and parent idle as background only.

## 6. Derived State Lifecycle

| Derived State | Created By | Source Requirement | Failure Behavior |
| --- | --- | --- | --- |
| summary | SummaryWorker | source message range | does not break chat |
| memory card | MemoryWorker or RelationshipWorker | source message ids | rejected without evidence |
| diary entry | DiaryWorker | source messages or memory ids | user-visible only after persisted |
| relationship memory | RelationshipWorker | Agent-authored idle evidence | cannot rewrite core persona |

Account-continuity rule:

- Account memory can enter every mode.
- Mode-private trace remains local until a worker promotes a concise, evidence-backed memory into account scope.

## 7. 代办

- Add exact runner state fields during V1.1 implementation.
