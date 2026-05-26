## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own product interaction flows that create user messages, build context, call the model, and save Agent replies.
- 架构思路
  - `conversations/` records what happened.
  - `interactions/` decides what happens next.
  - `context/` decides what the model should see.
- `model_runtime/` decides how to call the model.
- MVP reads fixed Agent persona records from `backend/agents/` until that module has persistence.

## responsibilities
- Run idle tick generation.
- Run companion_1 user-joins-idle generation.
- Run companion_2 user-message generation.
- Save user messages through `conversations/`.
- Read recent messages through `conversations/`.
- Build context through `context/`.
- Generate model replies through `model_runtime/`.
- Save Agent replies through `conversations/`.

## not responsible for
- Raw conversation/message persistence implementation.
- Model provider request details.
- Context recipe implementation.
- User-owned model settings.
- Long-term memory, diary, or relationship workers.

## folder structure
|-README.md interactions module guide
|-__init__.py Python package marker
|-routes.py FastAPI interaction routes
|-schemas.py interaction request and response schemas
|-service.py interaction orchestration logic
|-tests/ interaction tests

## route plan
|-POST /api/idle/{conversation_id}/tick generate one idle Agent reply
|-POST /api/idle/{conversation_id}/join create companion_1 turn from idle
|-POST /api/companion/{conversation_id}/messages append a companion_2 user message and generate Agent reply

## 代办
- Add speaker selection policy instead of fixed target Agent defaults.
- Add streaming support after the frontend is ready.
