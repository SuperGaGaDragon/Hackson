## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own future Work Mode task state and tool traces.
- 架构思路
  - V1.5 only reserves the Work Mode boundary.
  - The first production slice creates task state and lets a work conversation use that state in `context/`.
  - Full Planner / Worker / Reviewer collaboration belongs to v3.0.
  - Task memory must not pollute companion or idle memory.

## responsibilities
- Store task objectives and state.
- Store tool traces.
- Provide task state to the work context recipe.
- Keep Work Mode data isolated from companion context by default.

## not responsible for
- Idle life chat.
- Companion emotional memory.
- Agent persona editing.
- Immediate V1.0 chat flow.
- Full autonomous tool execution in early versions.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-model.py task and tool trace document helpers
|-repository.py MongoDB task persistence
|-routes.py FastAPI task routes
|-schemas.py task request and response schemas
|-service.py Work Mode task business rules
|-tests/ task module tests

## version plan
- v1.5: Add task state, minimal Work Mode message flow, and tool trace schemas.
- v3.0: Add Planner / Worker / Reviewer flow, tool execution queue, task summaries, failure retrospectives, and skill memory.

## isolation rule
- Work Mode content must not enter idle, companion_1, or companion_2 default context.

## minimum chain
- `POST /api/tasks` creates a task and a `work` conversation.
- `POST /api/tasks/{task_id}/messages` saves a user work message, builds `ContextMode.WORK`, calls the model runtime, and saves the Agent reply.
- Tool traces are stored as task-scoped derived records and are not executed autonomously in v1.5.
