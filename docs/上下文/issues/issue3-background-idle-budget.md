## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 3: Background Idle Budget

## Decision

Background Idle is user-controlled and defaults off.

Browser-closed generation may happen only when Background Idle is enabled and server-side budget, cooldown, and failure rules allow it.

## Risk

Unbounded Background Idle can create uncontrolled model cost, low-quality transcripts, summary pressure, memory pressure, and diary noise while the user is away.

## Constraints

- Background Idle belongs in Me or Idle settings.
- Enabling it must be explicit.
- Provider failures move the runner to cooldown.
- Server-side turn lock and idempotency must exist before Background Idle is implemented.
- Background generation must not bypass Context Package persistence.

## Required Tests

- Background Idle is off for new users.
- Browser-closed scheduled turns do not run when disabled.
- Enabled Background Idle respects budget.
- Rate limit moves runner to cooldown instead of retry loop.
- Multi-tab active sessions cannot duplicate the same next turn.
