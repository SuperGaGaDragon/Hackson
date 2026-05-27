## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 5: Streaming

## Problem

Users eventually need live progress for long model turns. V1.0 should not couple the correctness of the tool loop to streaming.

## Decision

V1.0 MUST use event polling only.

V1.2 SHOULD add streaming progress without changing the tool protocol.

## Risks

- Streaming partial JSON can be hard to validate.
- Partial tool content can fail mid-turn.
- UI may show text that later fails validation.
- Raw chain-of-thought must never leak.

## Constraints

- V1.0 MUST NOT require streaming.
- A V1.0 model turn becomes user-visible only after the tool call validates and persists.
- Future streaming MUST stream safe progress only.
- Future streaming MUST have polling fallback.
- Future streaming MUST NOT expose raw hidden reasoning.

## Possible V1.2 Shape

```text
MODEL_TURN_STARTED
MODEL_PROGRESS
TOOL_CALL_PROPOSED
TOOL_CALL_VALIDATED
TOOL_EXECUTED
MODEL_TURN_COMPLETED
```

## Acceptance

- V1.2 streaming can be disabled and the Mission still works through polling.
- Tool call validation remains authoritative.
