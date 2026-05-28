## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 4: Companion 1 Memory Scope

## Decision

Companion 1 may import two memory scopes:

- idle relationship memory for the parent Idle background.
- companion user memory for user preferences.

Work memory stays out by default.

## Risk

If Companion 1 imports only companion memory, it loses the living-world continuity of the parent Idle conversation. If it imports all idle memory blindly, it may over-prioritize Agent-Agent background over the user's current message.

## Constraints

- Current user message remains highest-priority content.
- Parent Idle memory is background only.
- Child companion transcript is direct conversation history.
- Work memory is excluded unless a future explicit recipe says otherwise.
- Memory cards require source message evidence.

## Required Tests

- Companion 1 prompt includes parent idle relationship memory when available.
- Companion 1 prompt includes companion user preference memory when relevant.
- Companion 1 prompt excludes Work memory.
- User message appears before background memory in priority.
