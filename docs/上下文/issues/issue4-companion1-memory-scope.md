## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 4: Companion 1 Memory Scope

## Superseded Note

Issue 11 updates the memory contract: Companion 1 now receives account memory by default, while legacy Companion user memory and Idle relationship memory are read as account-continuity input. This issue remains as historical context for the original Companion 1 import risk.

## Decision

Companion 1 may import two memory scopes:

- idle relationship memory for the parent Idle background.
- companion user memory for user preferences.

Raw Work trace and task-private Work memory stay out by default unless promoted into account memory.

## Risk

If Companion 1 imports only companion memory, it loses the living-world continuity of the parent Idle conversation. If it imports all idle memory blindly, it may over-prioritize Agent-Agent background over the user's current message.

## Constraints

- Current user message remains highest-priority content.
- Parent Idle memory is background only.
- Child companion transcript is direct conversation history.
- Raw Work trace is excluded unless a governed worker promotes a concise memory into account scope.
- Memory cards require source message evidence.

## Required Tests

- Companion 1 prompt includes parent idle relationship memory when available.
- Companion 1 prompt includes companion user preference memory when relevant.
- Companion 1 prompt excludes raw Work trace and task-private Work memory.
- User message appears before background memory in priority.
