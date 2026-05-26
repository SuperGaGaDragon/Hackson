## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own async derived work that should not block chat responses.
- 架构思路
  - The main conversation path must stay fast.
  - Workers generate summaries, memory candidates, diary entries, and relationship summaries after messages are saved.
  - The first production slice uses a small derived job record so interactions can enqueue work without knowing how each derived module works.
  - V1.0 can run without workers. Add them only when the main chain is stable.

## responsibilities
- Generate session and idle summaries.
- Generate memory candidates.
- Generate diary entries.
- Generate relationship summaries.
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
|-relationship_worker.py async relationship summary updates
|-derived_jobs.py derived job service and repository
|-tests/ worker tests

## version plan
- v1.2: Add `summary_worker.py`.
- v1.3: Add `memory_worker.py`.
- v1.4: Add `diary_worker.py` and `relationship_worker.py`.

## failure rule
- Worker failure must not break user chat.
- Derived outputs must be rebuildable from raw messages.
- A failed derived job records error metadata and can be retried without duplicating source messages.
