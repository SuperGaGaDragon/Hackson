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
  - V0 worker is deterministic and only emits structured events; it does not run shell commands or Codex CLI.
  - Routes expose `/api/work/*` while existing `/api/tasks` remains available until the Mission Runtime is verified.

## folder structure
|-README.md work_mode backend module guide
|-__init__.py Python package marker
|-model.py public response conversion helpers
|-schemas.py Pydantic request and response schemas
|-repository.py MongoDB persistence adapter
|-service.py Mission Runtime business rules and state transitions
|-worker.py deterministic V0 worker implementation
|-routes.py FastAPI routes for `/api/work`
|-tests/ work_mode unit and route tests

## state machine
- `draft` can start.
- `running` cannot start again.
- `running` can move to `stopping` through user stop.
- `stopping` becomes `stopped` when the worker observes it.
- V0 worker can move `running` to `completed` or `failed`.
- V0 smoke can set `HACKSON_WORK_MODE_V0_EVENT_DELAY_SECONDS` to make stop behavior observable; default is `0`.

## V0 limitations
- No Codex CLI execution.
- No arbitrary shell commands.
- No Git mutation.
- No production deploy actions.
- No WebSocket requirement; event polling is the first verified interface.

## 代办
- Replace FastAPI in-process background tasks with a durable worker queue in V1.
- Add artifacts and approvals after the event stream is verified.
