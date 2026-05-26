## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Hackson backend service. V1 starts with the user identity boundary and keeps each product capability in its own module.
- 架构思路
  - Use FastAPI as the HTTP layer.
  - Keep business modules split by domain, starting with `users/`.
  - Keep shared runtime concerns in `core/`.
  - Keep `conversations/` as the historical fact source for conversations and messages.
  - Keep `agents/` responsible for Agent identity, display profile, and persona source of truth.
  - Keep `interactions/` responsible for synchronous product flows after a user message or idle tick.
  - Keep `context/` responsible for what the model should see, and `model_runtime/` responsible for how the backend calls the model.
  - Keep `summaries/` responsible for persisted context compression records.
  - Keep `memory/` responsible for evidence-backed long-term memory cards.
  - Keep async derived work such as summary, memory, diary, and relationship updates under `workers/` when those features are introduced.
  - Use MongoDB as the persistence layer on the target machine.
  - V1 demo model endpoint is platform-managed and is not part of user data.
  - In production, FastAPI can also serve the built React frontend when `HACKSON_STATIC_FRONTEND_DIR` points at `frontend/dist`.

## folder structure
|-README.md backend folder guide
|-requirements.txt Python runtime dependencies
|-main.py FastAPI application entrypoint
|-core/ shared config, database, and security utilities
|-users/ user system module
|-agents/ agent persona and display-profile module
|-conversations/ conversation and message history module
|-interactions/ idle, companion_1, and companion_2 model interaction module
|-context/ context builder, recipes, transition context, compaction, and context packages
|-model_runtime/ platform-managed model configuration and model-call orchestration
|-summaries/ persisted summary records for context compression
|-workers/ async summary, memory, diary, and relationship workers
|-memory/ long-term memory cards and memory governance
|-diary/ user-visible Agent diary entries
|-tasks/ future Work Mode task and tool-trace module
|-tests/ cross-module backend app tests

## implementation status
- `core/`, `users/`, `agents/`, `conversations/`, `context/`, `model_runtime/`, and `interactions/` contain working V1 code.
- `workers/`, `memory/`, `summaries/`, `diary/`, and `tasks/` contain product-level module documentation and are implemented incrementally by tracer-bullet vertical slices.
- `main.py` mounts production frontend assets only when explicitly configured by deployment env.

## module boundaries
- `interactions/` owns the product flow: save input message when needed, ask `context/` for a context package, ask `model_runtime/` for a model response, save the Agent reply, and return it to the frontend.
- `agents/` owns the two fixed V1 Agent identities. Frontend display profiles and backend prompt persona records must come from this module.
- `conversations/` owns the historical fact source: conversation containers, message writes, message reads, sequence order, and ownership checks.
- `context/` owns context construction only. It should not directly call model providers or own HTTP routes.
- `model_runtime/` owns provider calls, timeout, retry, streaming, and platform-side model config. It should not know idle or companion business rules.
- `workers/` owns async derived data. It must not block the main chat response path.
- `summaries/`, `memory/`, `diary/`, and `tasks/` own persisted derived/product state. Context consumes their snapshots, not their storage implementations.

## 代办
- Add deployment scripts after the target port and process manager are finalized.
- Replace the fixed `agents/catalog.py` records after Agent persistence exists.
- Keep `docs/backend-architecture.md` updated when module boundaries change.
