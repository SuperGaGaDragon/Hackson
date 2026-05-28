## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own product interaction flows that create user messages, build context, call the model, and save Agent replies.
- 架构思路
  - `conversations/` records what happened.
  - `interactions/` decides what happens next.
  - `context/` decides what the model should see.
  - `orchestration/` decides Hackson mode policy before the model call.
  - `model_runtime/` decides how to call the provider.
- MVP reads fixed Agent persona records from `backend/agents/` until that module has persistence.

## responsibilities
- Run idle tick generation.
- Run idle user interjection generation in the same idle transcript.
- Decide the next idle speaking Agent from the saved transcript.
- Run companion_1 user-joins-idle generation.
- Run companion_1 continuation turns after the join-created child conversation exists.
- Run companion_2 user-message generation.
- Save user messages through `conversations/`.
- Read recent messages through `conversations/`.
- Read current user profile through `users/` for context only.
- Label user messages with the user's display name when building context.
- Label Agent messages with the user's two Agent profile names when building context.
- Build deterministic compact summaries when raw history exceeds the recent window.
- Build context through `context/`.
- Build and persist context packages through `ContextRuntime`.
- Read scoped active memory cards for context injection.
- Protect idle tick generation with a per-transcript turn lock before model generation.
- Gate future Background Idle with server-side setting, budget, and cooldown checks.
- Generate model replies through `orchestration/`, which delegates provider calls to `model_runtime/`.
- Convert model runtime failures into stable API errors before they reach the client.
- Save Agent replies through `conversations/`.
- Link saved Agent replies to `context_package_id`, `prompt_hash`, and safe model metadata.

## not responsible for
- Raw conversation/message persistence implementation.
- Model provider request details.
- Context recipe implementation.
- Context package persistence internals.
- User-owned model settings.
- Long-term memory, diary, or relationship worker execution.

## folder structure
|-README.md interactions module guide
|-__init__.py Python package marker
|-routes.py FastAPI interaction routes
|-schemas.py interaction request and response schemas
|-service.py interaction orchestration logic
|-locks.py idle turn lock repository and service
|-idle_cadence.py Background Idle eligibility policy and runner-state repository
|-tests/ interaction tests

## route plan
|-POST /api/idle/{conversation_id}/tick generate one idle Agent reply; accepts optional `discussionDirection`; backend chooses the next speaker from transcript
|-POST /api/idle/{conversation_id}/messages generate against the user interjection, then save user and Agent messages in the same idle conversation only after generation succeeds
|-POST /api/idle/{conversation_id}/join create companion_1 turn from idle
|-POST /api/companion/{conversation_id}/messages append a companion_1 or companion_2 user message and generate Agent reply

## 代办
- Add streaming support after the frontend is ready.
- Replace deterministic compact summaries with persisted worker summaries when summary worker is ready.
- Promote idle turn lock storage to a shared runner boundary when Background Idle starts.
