## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 11: Account-Level Agent Continuity

## Problem

Nora and Vale are product Agents owned by the user account, but the current memory contract treats Idle, Companion, and Work as mostly separate memory worlds. The visible result is that a direct Companion chat can answer like a fresh session even after the same user has used Idle or Work extensively.

This breaks the product promise. A top-tier companion product should make the user feel that the same Agents travel with them across modes. The Agents may change posture by mode, but they should not lose account-level knowledge of the user, their preferences, and durable shared history.

## Self Grill

Q: Should every raw Work trace enter Idle or Companion?

A: No. That would leak noisy task internals into casual conversation and make the Agents feel invasive. Raw task trace stays mode-private. Only governed, evidence-backed, account-visible memory crosses modes.

Q: Should Idle and Companion have separate personalities for Nora and Vale?

A: No. Agent profiles are account-level source data. Recipes may change mode behavior, but they must use the same user-owned Agent identity.

Q: Should user preferences learned in Companion be unavailable in Work?

A: No. Preferences such as language, tone, explanation style, and recurring goals are account-level. Work should use them unless the user disables or deletes the memory.

Q: Should relationship memory only matter inside Idle?

A: No. Relationship memory can help continuity everywhere when it is a concise relationship state, not a transcript dump. Work may use it lightly; Companion should use it to preserve the feel that Nora and Vale are the same pair.

Q: Is this only a prompt problem?

A: No. Prompt text currently receives scoped memory only because the interaction layer retrieves memory by mode and the recipe filters by scope. The fix needs a memory contract, retrieval path, recipe update, and regression tests.

## Decision

- Add an `account` memory scope for durable, user-account-visible memories.
- Inject account memory into Idle, Companion 1, Companion 2, and Work context recipes.
- Keep mode-specific private memory available only to the owning mode unless explicitly promoted or imported.
- Treat user facts and preferences from the MemoryWorker as account memory, not Companion-only memory.
- Preserve legacy Companion user memories by reading them as account-continuity input until migrated.
- Preserve Idle relationship memories by reading them as account-continuity input, while still hiding legacy filler cards.
- Do not share raw Work task trace with Idle or Companion. A later worker may promote completed Work outcomes into account memory with explicit evidence and provenance.

## Product Contract

Account continuity has four layers:

1. Agent profile: user-owned Nora and Vale names, voices, personalities, and stories. Always available across modes.
2. User profile: account basics, interaction style, and background. Always available when user-facing context is built.
3. Account memory: governed memory cards that can enter every mode.
4. Mode-private context: recent transcript, task state, tool trace, and local summaries. These stay in their mode unless converted into account memory.

## Acceptance

- Companion 2 receives account memory even when the memory was created outside the current conversation.
- Idle receives account memory while still excluding Companion-private memory that has not been promoted.
- Work receives account memory and Work-specific memory together.
- MemoryWorker writes explicit user preferences to `account` scope.
- Work turns enqueue memory-candidate jobs so explicit user facts and preferences learned during Work can become account memory.
- Existing Companion user preference cards remain visible through the account-continuity retrieval path.
- Existing Idle relationship cards remain visible through the account-continuity retrieval path unless they are deprecated filler memories.
- Regression tests prove the shared memory path and the private-mode boundary.
