## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own the Work Mode V0 Agent Mission Runtime backend module.
- 架构思路
  - Keep Mission Runtime separate from the older minimal `tasks/` Work chat module.
  - Store Projects, Missions, Runs, Steps, and Events in dedicated MongoDB collections.
  - Current Mission leads come from the authenticated user's two editable Agent profiles, `agent_1` and `agent_2`.
  - Legacy Employee collections and routes remain for compatibility, but the current product UI does not require Work-only Employee or Team setup.
  - V0 worker emitted deterministic structured events only.
  - V0.5 worker invokes the configured model runtime once, persists a bounded text Artifact, and emits a fixed `PRODUCT_UPDATED` event that points at that Artifact.
  - The worker delegates model execution to `model_runtime/`, including the configured target-machine Codex CLI provider when enabled.
  - V1.0 introduces a model-driven text Mission loop where the Lead Agent must choose exactly one validated tool per turn.
  - V1.0 tools are backend database actions only; shell, file, browser, and Codex CLI computer-control tools remain out of scope.
  - Routes expose `/api/work/*` while existing `/api/tasks` remains available until the Mission Runtime is verified.

## folder structure
|-README.md work_mode backend module guide
|-__init__.py Python package marker
|-model.py public response conversion helpers
|-schemas.py Pydantic request and response schemas
|-tool_protocol.py V1.0 model-visible tool action schemas and validation helpers
|-context.py V1.0 Lead and Delegate Agent context builders
|-action_client.py V1.0 JSON Action adapter around `model_runtime`
|-tool_executor.py V1.0 backend executor for validated model tool actions
|-loop.py V1.0 Lead Agent Mission loop runner
|-repository.py MongoDB persistence adapter
|-service.py Mission Runtime business rules and state transitions
|-worker.py V0.5 single-run model worker implementation
|-routes.py FastAPI routes for `/api/work`
|-tests/ work_mode unit and route tests

## state machine
- `draft` can start.
- `running` cannot start again.
- `running` can move to `stopping` through user stop.
- `stopping` becomes `stopped` when the worker observes it.
- V0.5 worker can move `running` to `completed` after persisting an Artifact, or to `failed` if the configured model runner fails.
- V0 smoke can set `HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS` to make stop behavior observable; default is `0`.

## V0.5 result contract
- `completed` means a runner returned output and `work_artifacts` contains the persisted result.
- V0.5 is a bounded first-pass contract. If the user requests a large deliverable such as an 8000-character story, the worker asks the model for a concise usable draft, sample, or outline instead of blocking one background request until the whole deliverable is complete.
- Mission detail returns `artifacts`, sorted newest first.
- `PRODUCT_UPDATED` event payload contains `artifactId`, `kind`, `summary`, `changedFiles`, and `tests`; full text lives in the Artifact, not in the event payload.
- If the model provider returns a stable failure such as timeout or rate limit, the Mission and active Step are marked `failed` and no fake Artifact is created.

## V0.5 limitations
- No direct Work Mode shell execution; model calls go through `model_runtime/`.
- No arbitrary shell commands.
- No Git mutation.
- No production deploy actions.
- No WebSocket requirement; event polling is the first verified interface.
- No multi-step supervisor loop yet.
- No guaranteed full long-form generation in one run; that belongs in the later supervisor loop.

## V1.0 target contract
- The model must return one tool action per Lead Agent turn.
- Plain assistant text is invalid.
- Natural language belongs inside tool arguments only.
- Backend validation owns tool schema, Product references, Artifact references, and Mission state compatibility.
- First tool protocol implementation uses provider-agnostic JSON Action; provider-native tool calling is a later adapter over the same backend schema.

## 代办
- Implement V1.0 Product, Artifact lineage, Work Window, context, and loop layers from `docs/work_mode/final_version.md`.
- Replace FastAPI in-process background tasks with a durable worker queue after V1.0 is proven.
