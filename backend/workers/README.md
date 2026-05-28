## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own async derived work that should not block chat responses.
- 架构思路
  - The main conversation path must stay fast.
  - Workers generate summaries, memory candidates, diary entries, and relationship summaries after messages are saved.
- The first production slice uses a small derived job record so interactions can enqueue work without knowing how each derived module works.
- V1.0 can run without workers, but product-grade continuity requires a bounded worker loop once Memory and persisted Summary are visible.
- Scoped processing exists for smoke and diagnostics so a fresh user's jobs are not blocked by historical backlog.
- Background processing uses both FIFO and a latest-pending freshness lane, so new conversations keep learning while old backlog drains.

## responsibilities
- Generate session and idle summaries.
- Generate account memory candidates from explicit user-authored facts and preferences in Companion or Work.
- Generate diary entries.
- Generate relationship summaries only when enough Agent-message evidence exists.
- Retry derived work when safe.

## not responsible for
- Synchronous chat responses.
- HTTP routing.
- User authentication.
- Direct frontend responses.
- Core conversation state transitions.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-summary_worker.py async summary generation
|-memory_worker.py async memory candidate generation
|-diary_worker.py async diary generation
|-relationship_worker.py evidence-backed relationship summary updates
|-derived_jobs.py derived job service and repository
|-runner.py compose concrete workers into one product runner pass and optional background loop
|-tests/ worker tests

## version plan
- v1.2: Add `summary_worker.py`.
- v1.3: Add `memory_worker.py`.
- v1.4: Add `diary_worker.py` and `relationship_worker.py`.
- v1.5: Add `runner.py` so target smoke can process queued derived jobs without each caller wiring handlers manually.
- v1.6: Add scoped job processing and an opt-in process-local worker loop for production freshness.

## failure rule
- Worker failure must not break user chat.
- Derived outputs must be rebuildable from raw messages.
- A failed derived job records error metadata and can be retried without duplicating source messages.
- Current-user smoke must not require draining unrelated pending jobs.
- New pending jobs must not be starved behind old backlog.
