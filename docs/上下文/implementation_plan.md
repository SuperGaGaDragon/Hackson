## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Lst Modified by: Codex

# Context Runtime Implementation Plan

## 1. Purpose

This document is the engineer-facing build order for Context Runtime.

Follow this plan after reading `final_version.md`, `architecture.md`, `state_machine.md`, `context_package.md`, and `ui_contract.md`.

## 2. Preflight

Before implementation:

```bash
git status --short
find docs/上下文 -maxdepth 2 -type f | sort
```

Rules:

- Do not edit files under `docs/上下文/legacy/` except for legacy notices.
- Do not change target-machine services until local tests pass.
- Do not update `api.md` until verified behavior exists.
- Do not expose raw chain-of-thought.

## 3. Loop 1: Context Package Persistence

Implement a persistence boundary for context package metadata.

This is the V1.0 release gate. Do not start server-owned Idle cadence or governed memory work until this loop is complete enough to reproduce a poor model turn from persisted context package metadata and source ids.

Likely files:

- `backend/context/packages.py`
- `backend/context/repository.py`
- `backend/context/service.py`
- `backend/context/tests/`
- `backend/context/README.md`

Required tests:

- New users default to Full Prompt Logging enabled.
- Full prompt text retention policy is 30 days.
- Package metadata persists with source ids.
- Prompt hash is deterministic.
- Included ids match recipe input.
- Full prompt text is persisted only when Full Prompt Logging is enabled.
- Full prompt text is omitted when Full Prompt Logging is disabled.
- Turning Full Prompt Logging off does not delete existing retained prompt text.
- Delete Prompt Logs clears retained full prompt text but leaves package metadata.
- Users cannot edit historical full prompt text.

Exit criteria:

- Idle Tick stores a package record linked to the assistant message metadata.
- The current user can control Full Prompt Logging from Me before a package is created.
- The current user can delete retained full prompt text from Me.

## 4. Loop 2: Context Runtime Facade

Create or deepen a single interface used by `interactions/`.

Decision:

- Implement `ContextRuntime` as a facade around existing `ContextBuilder`, package persistence, and source loading.

Required behavior:

- Build package.
- Persist metadata.
- Return model-ready messages.
- Keep existing `ContextBuilder` tests passing.

Exit criteria:

- `InteractionService` no longer needs to know package persistence details.

## 5. Loop 3: Idle Turn Lock And Idempotency

Add server-side protection for duplicate turns.

Required tests:

- Two simultaneous ticks cannot create two next-Agent turns from the same transcript.
- Retried request with same idempotency key returns the same result or stable conflict.
- Lock release happens after success or failure.

Exit criteria:

- Multi-tab smoke cannot duplicate the same idle turn.

## 6. Loop 4: Background Idle Setting And Cadence

Add user-controlled Background Idle after turn locking exists.

Required tests:

- Background Idle defaults off.
- Background Idle disabled prevents browser-closed scheduled turns.
- Background Idle enabled allows scheduled turns only inside budget.
- Provider failure moves runner to cooldown.
- User can change Background Idle setting from Me or Idle settings.

Exit criteria:

- Browser-closed idle generation happens only when the user enabled Background Idle.

## 7. Loop 5: Worker Runner

Make derived jobs actually run in a controlled backend process or management command.

Required behavior:

- Summary jobs run.
- Memory jobs run.
- Failed jobs record error metadata.
- Production starts a bounded process-local derived worker loop when enabled by platform settings.
- Smoke and diagnostics can process jobs scoped to a current user/conversation without draining unrelated backlog.
- Background worker loops include a latest-pending freshness lane so current users are not starved by old backlog.
- Chat path remains unaffected.

Exit criteria:

- A saved user preference can create a memory card through the worker path.

## 8. Loop 6: Persisted Summary Selection

Replace synchronous compact as the primary long-history source.

Required tests:

- Conversation over 50 turns includes latest raw messages.
- Older source range enters via persisted summary.
- Summary source ids are auditable.

Exit criteria:

- Context package debug notes identify summary source.

## 9. Loop 7: Memory Controls And Scope Rules

Expose governed memory to context and UI.

V1.3 public release requires Memory Control. V1.0 does not.

Required tests:

- Account memory enters Companion 2, Idle, and Work.
- Companion 1 imports account memory plus parent Idle background.
- Legacy companion user memory and idle relationship memory remain readable through account-continuity retrieval.
- Work turns enqueue memory-candidate jobs so explicit user preferences learned during Work become account memory.
- Raw Work trace and task-private memory stay out of Idle and Companion.
- User can disable or delete a memory.

Exit criteria:

- Public UI has a minimal memory control surface or the release is explicitly marked internal-only.

## 10. Loop 8: Context Eval Gate

Add deterministic qualitative eval fixtures.

Required dimensions:

- mode fit.
- speaker boundary.
- topic adherence.
- repetition.
- transition quality.
- memory use.
- latency note.

Exit criteria:

- Context changes run the fixed eval set before target-machine smoke.

## 11. Loop 9: Idle Interruption Queue

Required behavior:

- Idle composer stays enabled while generation is in flight.
- Sending during generation creates a pending queued user line.
- Queued Idle Say runs immediately after the current turn settles.
- Auto pauses while queued user input exists.
- Backend protects Idle Say with per-transcript lock and idempotency key.

Required tests:

- UI smoke verifies input is enabled during Working.
- Interaction service test verifies simultaneous Idle Say/Idle Tick conflict returns `idle_turn_locked`.
- Same Idle Say idempotency key returns the same saved user/Agent pair.

Exit criteria:

- User can interrupt without duplicate transcript writes.

## 12. Loop 10: Human Idle Dialogue Recipe

Required behavior:

- Idle prompt includes Relationship Stance.
- Idle prompt includes one Turn Intent.
- Idle prompt asks the Agent to respond to the previous Agent's concrete line.
- Idle prompt blocks stacked advice/checklists by default.
- Idle prompt includes Collaborative Convergence Protocol.
- Idle prompt requires agreement acknowledgment, decision-relevant disagreement, non-repetition, shared-conclusion checks, and an emphasis-only stop condition.
- Idle prompt explicitly prioritizes a user interjection over Agent-Agent convergence.
- Context eval covers the human dialogue contract.

Exit criteria:

- Eval and HTTP prompt-log smoke prove the prompt contract is active before production deployment.

## 13. Loop 11: Me Page Product IA And Memory Quality

Required behavior:

- `Me` first viewport prioritizes account basics and Agent editing.
- User profile context is labeled `Style` and `Background`.
- Memory controls are compact and below profile editing.
- Nora and Vale seed with detailed editable Agent Origin Stories instead of one-line demo status text.
- Prompt Logs live inside collapsed `Debug`.
- Prompt Logs remain expandable and readable after opening Debug.
- Relationship worker does not generate generic filler cards.
- Relationship memory uses source message evidence and requires enough Agent evidence.
- Idle relationship job enqueueing includes the current Agent message and the previous Agent message when available.
- Deprecated generic relationship cards are hidden from user-facing memory reads.
- Current-user derived work can run even when old pending jobs exist.

Required tests:

- Frontend smoke verifies Debug collapsed by default.
- Frontend smoke verifies Agent editor appears before prompt log rows.
- Frontend smoke opens Debug and expands a prompt log.
- Worker tests reject one-message/generic relationship memories.
- Worker tests accept relationship memory with content-derived summary.
- Worker tests cover scoped job processing.
- Worker tests cover latest-pending freshness processing.
- Memory tests hide deprecated generic relationship cards.

Exit criteria:

- Public `Me` feels like a product settings page, not an internal prompt dump.
- Public API smoke proves summary, memory, diary, and relationship jobs complete for the current user.

## 14. 代办

- Keep Loop 1 as the first implementation step.
- Add exact API shapes to `api.md` only after verified implementation exists.

## 15. Loop 12: Idle Brainstorm Card To Work Mission

Required behavior:

- Backend exposes an Idle Brainstorm Card endpoint built from visible raw Idle messages.
- Card response includes topic, key ideas, disagreements, decision, open questions, suggested Mission title/goal, generated time, source message count, and source message ids.
- Backend rejects non-Idle conversations.
- Frontend Idle right rail can build and refresh the card.
- Frontend promotion modal lets the user choose an existing Project or create a new Project.
- Frontend lets the user edit Mission title, Mission goal, and Lead Agent.
- Promotion calls the existing Work Mission create API and stores Idle provenance metadata.
- Created Mission remains draft until the user starts it in Work.

Required tests:

- Interaction route or service test covers card generation and source ids.
- Interaction route or service test rejects non-Idle conversation.
- Frontend build passes.
- Target-machine API smoke creates an Idle conversation, builds a card, creates/promotes a draft Mission on a non-public port, and confirms Mission metadata.

Exit criteria:

- A user can discuss in Idle, convert the discussion into a concise brief, edit the Work draft, create a Mission, and jump to Work without copying text manually.

## 16. Loop 13: Idle Right Rail Product Polish

Required behavior:

- Right rail default view prioritizes Target Agent, Topic, and Brainstorm action.
- Brainstorm appears before secondary Session metadata.
- Session metadata is compact and limited to user-comprehensible state such as Auto and Status.
- Turn count appears only inside collapsed Debug when needed.
- Raw conversation ids and parent ids are hidden behind collapsed Debug.
- No standalone `ID` or `Count` object cards appear in the normal right rail.

Required tests:

- Frontend build passes.
- Target public static asset smoke confirms the updated bundle is served.

Exit criteria:

- Idle right rail feels like a user control surface, not an internal inspector.
