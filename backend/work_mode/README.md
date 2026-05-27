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
  - V0.5 worker invokes the configured model runtime once, persists a text Artifact, and emits a fixed `PRODUCT_UPDATED` event that points at that Artifact.
  - The worker delegates model execution to `model_runtime/`, including the configured target-machine Codex CLI provider when enabled.
  - Routes expose `/api/work/*` while existing `/api/tasks` remains available until the Mission Runtime is verified.

## folder structure
|-README.md work_mode backend module guide
|-__init__.py Python package marker
|-model.py public response conversion helpers
|-schemas.py Pydantic request and response schemas
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
- Mission detail returns `artifacts`, sorted newest first.
- `PRODUCT_UPDATED` event payload contains `artifactId`, `kind`, `summary`, `changedFiles`, and `tests`; full text lives in the Artifact, not in the event payload.
- If the model provider returns a stable failure such as rate limit, the Mission is marked `failed` and no fake Artifact is created.

## V0.5 limitations
- No direct Work Mode shell execution; model calls go through `model_runtime/`.
- No arbitrary shell commands.
- No Git mutation.
- No production deploy actions.
- No WebSocket requirement; event polling is the first verified interface.
- No multi-step supervisor loop yet.

## 代办
- Replace FastAPI in-process background tasks with a durable worker queue in V1.
- Add approvals after artifact generation is verified on the public service.
