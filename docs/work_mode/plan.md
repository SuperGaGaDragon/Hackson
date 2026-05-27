## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

# Work Mode V0 Implementation Plan

## 1. Purpose

This document is the implementation manual for Work Mode V0.

A developer who has never seen this repository should be able to follow this plan and build the first Agent Mission Runtime slice without guessing product behavior, file ownership, data shape, or verification steps.

V0 must not attempt to build the full autonomous Codex workflow or editable Employee roster. V0 must build the smallest reliable runtime foundation:

```text
Create Project
  -> Create Mission
  -> Start Mission
  -> Worker emits structured events
  -> Frontend renders Mission console
  -> User can stop Mission
  -> Mission reaches completed, failed, or stopped
```

## 2. Required Reading

Read these files before implementation:

1. `agents/restrictions.md`
2. `agents/frontend_restrictions.md`
3. `README.md`
4. `api.md`
5. `docs/backend-architecture.md`
6. `docs/deployment/production.md`
7. `docs/work_mode/versions.md`
8. `docs/work_mode/brainstorm.md`
9. `backend/README.md`
10. `frontend/README.md`
11. `frontend/src/README.md`

Important repository rules:

- Check `git status --short` before work.
- Do not stop existing target-machine services.
- Use new ports for smoke tests.
- Every new folder needs a `README.md`.
- Every new source file needs the project header.
- Update `api.md` only after API verification.
- Frontend copy must be short.

## 3. Current Baseline

The current Work implementation is minimal:

- `backend/tasks/` creates a task and a linked `work` conversation.
- `POST /api/tasks/{taskId}/messages` sends one model-backed Work message.
- `frontend/src/features/work/WorkPage.jsx` shows task list, transcript, and composer.
- Production on target machine has verified `/api/tasks` and Work message APIs.

V0 must not delete this baseline until the Mission Runtime replacement is verified.

Use the existing `tasks` module as reference only. Do not force the Mission Runtime into the old task schema.

## 4. Product Definition

### 4.1 Names

Use these product terms consistently:

- Workspace: the whole product account scope. V0 can treat this as implicit current user scope.
- Project: a repo or work target.
- Mission: a user goal inside one Project.
- Run: one execution attempt for a Mission.
- Step: one runtime action inside a Run.
- Event: one persisted user-visible update.
- Artifact: a persisted result such as log, diff, report, or final product.
- Approval: a user decision required before risky continuation.

### 4.2 V0 User Flow

1. User opens Work.
2. User creates a Project with name only.
3. User creates a Mission under that Project with a goal.
4. System selects a Lead Agent from the two user-owned Agent profiles.
5. User opens Mission detail.
6. User clicks Start.
7. Backend creates a Run.
8. Worker appends events.
9. UI updates timeline and panels.
10. User can click Stop.
11. Mission ends as completed, failed, or stopped.

Project creation rule:

- `name` is required.
- `repoPath` is optional runtime metadata and must not block creating a workspace Project.
- The frontend New Project form only asks for `Project`.
- Backend responses keep `repoPath` as an empty string when no path is provided, for compatibility with existing response shapes.

### 4.3 V0 UI Must Show

Left:

- Workspace project list.
- New Project with name only.
- Mission list for selected Project.
- Create Mission.

Center:

- Mission title and status.
- Current step.
- Progress timeline.
- Summary cards.
- Product panel.

Right:

- Inspector.
- Warnings.
- Approval panel in disabled V0 state.
- Runtime policy summary.

Bottom:

- Raw logs.

### 4.4 V0 Non Goals

Do not implement these in V0:

- Full Codex autonomous loop.
- Separate Work-only Employee creation.
- Multi-Agent brainstorm.
- Agent-to-Agent tool calls.
- Multi-agent Worker/Reviewer.
- Git push.
- Deploy.
- Production mutation.
- Arbitrary shell command input from user.
- User-defined agent graph.
- Long-term skill memory.
- Desktop pet integration.

## 5. Architecture

### 5.1 Target Shape

```text
React Work UI
  -> FastAPI Work Runtime routes
    -> WorkRuntimeService
      -> ProjectRepository
      -> MissionRepository
      -> RunRepository
      -> StepRepository
      -> EventRepository
      -> WorkerLauncher
        -> MissionWorker
          -> EventRepository
```

### 5.2 Runtime Responsibility Split

Routes:

- Parse HTTP input.
- Authenticate current user.
- Call service.
- Return public shapes.

Service:

- Enforce ownership.
- Validate state transitions.
- Create Project, Mission, Run, Step, Event documents.
- Start and stop Missions.
- Decide whether a Mission can be started.

Repositories:

- Own MongoDB collections and indexes.
- Convert ids safely.
- Return raw documents only to service.

WorkerLauncher:

- Starts V0 worker execution.
- V0 may use in-process background tasks first.
- Later versions can replace it with process queue or external worker.

MissionWorker:

- Emits deterministic V0 events.
- Emits the selected Lead Agent in event payloads.
- Does not call arbitrary shell in the first slice.
- Later can call Codex runner through a controlled adapter.

Frontend:

- Renders fixed components by event type.
- Does not parse raw model text for UI structure.
- Does not expose dangerous command input.

## 6. Backend Module Plan

### 6.1 New Module

Create:

```text
backend/work_mode/
  README.md
  __init__.py
  model.py
  schemas.py
  repository.py
  service.py
  routes.py
  worker.py
  tests/
    README.md
    test_work_mode_service.py
    test_work_mode_routes.py
```

Reason:

- Keep Mission Runtime separate from existing minimal `tasks/`.
- Avoid breaking verified `/api/tasks` while V0 is under construction.
- Create a deeper module whose interface is Mission-oriented.

### 6.2 backend/work_mode/README.md

Document:

- Module goal.
- Module responsibilities.
- Folder structure.
- State machine.
- V0 limitations.

### 6.3 backend/work_mode/model.py

Public conversion helpers only.

Required helpers:

- `public_project(document)`
- `public_mission(document)`
- `public_run(document)`
- `public_step(document)`
- `public_event(document)`
- `now_utc()` can be imported from `conversations.model`

Public shapes must use camelCase keys for frontend.

### 6.4 backend/work_mode/schemas.py

Define Pydantic request and response models.

Required literals:

```python
ProjectStatus = Literal["active", "archived"]
MissionStatus = Literal["draft", "running", "paused", "stopping", "stopped", "blocked", "failed", "completed"]
RunStatus = Literal["running", "stopped", "failed", "completed"]
StepStatus = Literal["pending", "running", "failed", "completed", "skipped"]
EventType = Literal[
    "MISSION_CREATED",
    "MISSION_STARTED",
    "STEP_STARTED",
    "SUMMARY",
    "WARNING",
    "RAW_LOG",
    "PRODUCT_UPDATED",
    "STEP_COMPLETED",
    "MISSION_STOP_REQUESTED",
    "MISSION_STOPPED",
    "MISSION_COMPLETED",
    "MISSION_FAILED",
]
```

Required request models:

- `ProjectCreateRequest`
  - `name`: 1 to 120 chars
  - `repo_path`: optional internal field, alias `repoPath`
  - `metadata`: dict

- `MissionCreateRequest`
  - `project_id`: alias `projectId`
  - `title`: 1 to 160 chars
  - `goal`: 1 to 8000 chars
  - `lead_employee_id`: alias `leadEmployeeId`, default `employee_default_lead`
  - current UI sends user Agent slots `agent_1` or `agent_2`
  - `supporting_employee_ids`: alias `supportingEmployeeIds`, default `[]`
  - `autonomy_level`: alias `autonomyLevel`, default `"supervised"`
  - `max_iterations`: alias `maxIterations`, default `1`, min `1`, max `20`
  - `metadata`: dict

- `MissionStartRequest`
  - `metadata`: dict

- `MissionStopRequest`
  - `reason`: optional 1000 chars

Required response models:

- `ProjectResponse`
- `MissionResponse`
- `RunResponse`
- `StepResponse`
- `EventResponse`
- `MissionDetailResponse`

### 6.5 backend/work_mode/repository.py

MongoDB collections:

- `work_projects`
- `work_missions`
- `work_runs`
- `work_steps`
- `work_events`

V0 lead rule:

- Current Mission leads are the two user-owned Agents edited in `Me`.
- Store `lead_employee_id`, `lead_employee_name`, `lead_employee_role`, and `supporting_employee_ids` as Mission fields or metadata.
- Accept `agent_1` and `agent_2` as direct Mission leads for the authenticated user.
- Keep the legacy default Lead for old Missions and API compatibility:
  - id: `employee_default_lead`
  - name: `Lead`
  - role: `Mission lead`

Indexes:

```text
work_projects:
  user_id + status + updated_at desc
  user_id + name

work_missions:
  user_id + project_id + status + updated_at desc
  user_id + status + updated_at desc
  user_id + lead_employee_id + updated_at desc

work_runs:
  user_id + mission_id + started_at desc

work_steps:
  user_id + run_id + sequence asc
  user_id + mission_id + sequence asc

work_events:
  user_id + mission_id + sequence asc unique
  user_id + run_id + sequence asc
  user_id + mission_id + created_at desc
```

Repository methods:

- `ensure_indexes()`
- `create_project(document)`
- `find_project(project_id, user_id)`
- `list_projects(user_id, limit)`
- `create_mission(document)`
- `find_mission(mission_id, user_id)`
- `list_missions(user_id, project_id, limit)`
- `update_mission(mission_id, user_id, values)`
- `create_run(document)`
- `find_active_run(mission_id, user_id)`
- `update_run(run_id, user_id, values)`
- `create_step(document)`
- `update_step(step_id, user_id, values)`
- `next_event_sequence(mission_object_id)`
- `create_event(document)`
- `list_events(user_id, mission_id, after_sequence, limit)`

Implementation detail:

- Use ObjectId validation like existing repositories.
- Use a `work_event_counters` collection or atomic query to guarantee event sequence.
- Prefer `work_event_counters` for clarity.

### 6.6 backend/work_mode/service.py

Service methods:

- `create_project(user_id, payload)`
- `list_projects(user_id, limit)`
- `create_mission(user_id, payload)`
- `list_missions(user_id, project_id, limit)`
- `get_mission_detail(user_id, mission_id)`
- `start_mission(user_id, mission_id, payload)`
- `stop_mission(user_id, mission_id, payload)`
- `list_events(user_id, mission_id, after_sequence, limit)`
- `append_event(user_id, mission, run, event_type, title, message, payload)`

State rules:

- `draft`, `paused`, `stopped`, `failed`, `completed`, `blocked` can be started.
- `running` cannot be started again.
- `stopping` cannot be started.
- Stop is valid only for `running`.
- V0 worker must check Mission status before appending terminal events.

Start behavior:

1. Load Mission and Project.
2. Validate Project belongs to user.
3. Set Mission status to `running`.
4. Create Run with status `running`.
5. Append `MISSION_STARTED`.
6. Ask WorkerLauncher to run V0 worker.
7. Return Mission detail.

Stop behavior:

1. Validate Mission is `running`.
2. Set Mission status to `stopping`.
3. Append `MISSION_STOP_REQUESTED`.
4. V0 worker observes status and writes `MISSION_STOPPED`.
5. If no worker is active, service can mark stopped directly.

### 6.7 backend/work_mode/worker.py

V0 worker is deterministic.

Function:

```python
def run_v0_mission(user_id: str, mission_id: str, run_id: str) -> None:
    ...
```

V0 event sequence:

1. Create Step `Inspect mission`.
2. Event `STEP_STARTED`.
3. Event `SUMMARY` with mission goal and repo path.
4. Event `RAW_LOG` with a short deterministic message.
5. Event `PRODUCT_UPDATED` with a V0 product summary.
6. Mark Step completed.
7. Event `STEP_COMPLETED`.
8. Mark Run completed.
9. Mark Mission completed.
10. Event `MISSION_COMPLETED`.

Stop check:

- Before each event group, reload Mission.
- If status is `stopping`, mark step skipped or stopped, mark run stopped, mark mission stopped, append `MISSION_STOPPED`, return.

V0 BackgroundTasks:

- FastAPI `BackgroundTasks` is acceptable for V0.
- It is not acceptable for V1 long-running loops.
- Document this limitation in `backend/work_mode/README.md`.

### 6.8 backend/work_mode/routes.py

Mount under:

```text
/api/work
```

Routes:

- `POST /api/work/projects`
- `GET /api/work/projects`
- `POST /api/work/missions`
- `GET /api/work/projects/{projectId}/missions`
- `GET /api/work/missions/{missionId}`
- `POST /api/work/missions/{missionId}/start`
- `POST /api/work/missions/{missionId}/stop`
- `GET /api/work/missions/{missionId}/events`

V0 streaming:

- Polling with `afterSequence` is acceptable first.
- SSE can be added after polling is verified.
- Do not block V0 on WebSocket.

### 6.9 backend/main.py

Add:

```python
from work_mode.routes import router as work_mode_router
app.include_router(work_mode_router, prefix="/api/work", tags=["work-mode"])
```

Do not remove existing `tasks_router`.

## 7. Frontend Plan

### 7.1 New Frontend Structure

Create or update:

```text
frontend/src/api/workMode.js
frontend/src/features/work/WorkPage.jsx
frontend/src/features/work/components/
  README.md
  MissionHeader.jsx
  ProjectMissionRail.jsx
  ProgressTimeline.jsx
  SummaryCard.jsx
  WarningCard.jsx
  ProductPanel.jsx
  ApprovalCard.jsx
  RawLogPanel.jsx
  InspectorPanel.jsx
```

V0 may keep all components in `WorkPage.jsx` only if speed is critical, but product quality is better with small feature-local components.

### 7.2 API Client

`frontend/src/api/workMode.js` functions:

- `createProject(payload)`
- `listProjects()`
- `createMission(payload)`
- `listProjectMissions(projectId)`
- `getMission(missionId)`
- `startMission(missionId)`
- `stopMission(missionId, payload)`
- `listMissionEvents(missionId, afterSequence)`

Use existing `apiRequest`.

### 7.3 WorkPage State

Required state:

- `projects`
- `selectedProject`
- `missions`
- `selectedMission`
- `events`
- `afterSequence`
- `loading`
- `busy`
- `error`
- `agents`
- `missionLeadId`
- `newProjectName`
- `newMissionTitle`
- `newMissionGoal`

Workspace-first rule:

- Initial Work load must not auto-open the first Project.
- Initial Work load shows the Workspace screen with Project list and New Project only.
- Selecting a Project loads Missions, selected Mission, and events.
- Creating a Project may open that Project detail after successful persistence.
- Returning to Workspace clears the selected Project and selected Mission from the visible UI.

### 7.4 Polling

V0 polling rule:

- If selected Mission status is `running` or `stopping`, poll events every 1500 ms.
- Use `afterSequence` to fetch only new events.
- Stop polling when terminal status is `completed`, `failed`, `stopped`, or `blocked`.

Terminal status list:

```js
const terminalMissionStatuses = new Set(["completed", "failed", "stopped", "blocked"]);
```

### 7.5 Event Rendering

Map event types to fixed UI:

| Event type | Component |
| --- | --- |
| `MISSION_STARTED` | `ProgressTimeline` |
| `STEP_STARTED` | `ProgressTimeline` |
| `SUMMARY` | `SummaryCard` |
| `WARNING` | `WarningCard` |
| `RAW_LOG` | `RawLogPanel` |
| `PRODUCT_UPDATED` | `ProductPanel` |
| `STEP_COMPLETED` | `ProgressTimeline` |
| `MISSION_COMPLETED` | `ProductPanel` |
| `MISSION_FAILED` | `WarningCard` |
| `MISSION_STOP_REQUESTED` | `ProgressTimeline` |
| `MISSION_STOPPED` | `ProgressTimeline` |

### 7.6 Copy Rules

Keep text short.

Use:

- `Projects`
- `Missions`
- `Start`
- `Stop`
- `Running`
- `Done`
- `Stopped`
- `Logs`
- `Product`
- `Warnings`
- `Approval`
- `Inspector`

Avoid:

- Long explanations.
- Marketing hero copy.
- Chatbot-style empty state paragraphs.

### 7.7 Visual Layout

Use the current app shell.

Project detail grid:

```text
left rail      center mission console       right inspector
agents        header                       status
missions      timeline                     warnings
create        summary/product              approvals
              bottom raw logs
```

Workspace screen:

```text
workspace
projects grid
new project form
```

Do not build a marketing landing page.

Do not show Agents, Mission, console, Inspector, or raw logs on the Workspace screen.

## 8. Event Payload Contract

All events have:

```json
{
  "id": "string",
  "missionId": "string",
  "runId": "string or null",
  "stepId": "string or null",
  "sequence": 1,
  "type": "SUMMARY",
  "title": "string",
  "message": "string",
  "payload": {},
  "createdAt": "iso datetime"
}
```

V0 payload examples:

`SUMMARY`:

```json
{
  "employee": {
    "id": "employee_default_lead",
    "name": "Lead",
    "role": "Mission lead"
  },
  "items": [
    "Mission loaded",
    "Project state loaded",
    "V0 worker completed"
  ]
}
```

`WARNING`:

```json
{
  "severity": "medium",
  "suggestedNextStep": "Check worker logs"
}
```

`RAW_LOG`:

```json
{
  "employee": {
    "id": "employee_default_lead",
    "name": "Lead",
    "role": "Mission lead"
  },
  "stream": "stdout",
  "text": "V0 worker inspected mission state."
}
```

`PRODUCT_UPDATED`:

```json
{
  "employee": {
    "id": "employee_default_lead",
    "name": "Lead",
    "role": "Mission lead"
  },
  "kind": "mission_result",
  "summary": "V0 Mission Runtime completed a deterministic worker run.",
  "changedFiles": [],
  "tests": "not_run"
}
```

## 9. Runtime Safety Policy

V0:

- No arbitrary user command execution.
- No unsupervised user Agent execution.
- No Agent-to-Agent tool calls.
- No production write operations beyond database records for the logged-in user.
- No Git mutation.
- No file mutation by worker.

V0.5 and later:

- Add command allowlist.
- Add forbidden command filter.
- Add repo path validation.
- Add worktree isolation.
- Add approval gates.

V1.25 and later:

- Add supporting Agent brainstorm.
- Add Agent provenance to every model-generated event.
- Add Project-level Agent memory only after the V0 lead flow is stable.

Never allow:

- `rm -rf /`
- writing outside approved repo/worktree
- pushing to remote without approval
- deployment without approval
- reading or displaying secrets in UI

## 10. Implementation Steps

### Step 0: Preflight

Commands:

```bash
git status --short
find docs/work_mode -maxdepth 1 -type f -print
```

Expected:

- Existing worktree state is understood.
- `docs/work_mode/README.md`, `versions.md`, and `plan.md` exist.

### Step 1: Backend Work Mode Module Skeleton

Create files:

- `backend/work_mode/README.md`
- `backend/work_mode/__init__.py`
- `backend/work_mode/model.py`
- `backend/work_mode/schemas.py`
- `backend/work_mode/repository.py`
- `backend/work_mode/service.py`
- `backend/work_mode/worker.py`
- `backend/work_mode/routes.py`
- `backend/work_mode/tests/README.md`

Acceptance:

- Files have headers.
- `python -m py_compile` passes for new files.

### Step 2: Schemas and Public Models

Implement schemas and `public_*` helpers.

Tests:

- Instantiate each request and response model.
- Validate empty project name fails.
- Validate invalid Mission status fails.

Acceptance:

- Schema tests pass with `python -m unittest discover -s work_mode/tests -p 'test*.py'`.

### Step 3: Repository

Implement Mongo repository and indexes.

Tests:

- Use in-memory fake repository for service tests.
- Do not require Mongo for unit tests.
- Add one integration smoke later on target machine.

Acceptance:

- Repository imports without opening Mongo.
- Index creation is called by service init.

### Step 4: Service State Machine

Implement Project and Mission service methods.

Tests:

- Create Project.
- List Projects.
- Create Mission under owned Project.
- Reject Mission under missing Project.
- Start draft Mission.
- Reject double start.
- Stop running Mission.
- Reject stop for draft Mission.
- List events after sequence.

Acceptance:

- State transitions match Section 6.6.

### Step 5: V0 Worker

Implement deterministic worker.

Tests:

- Starting Mission creates Run.
- Worker emits expected event sequence.
- Worker completes Mission.
- If Mission is `stopping`, worker emits `MISSION_STOPPED`.

Acceptance:

- A full in-memory service test proves end-to-end V0 event sequence.

### Step 6: Routes

Implement `/api/work` routes.

Tests:

- Route test with FastAPI `TestClient`.
- Override auth dependency to a test user.
- Override service dependency with fake service if needed.

Acceptance:

- `POST /api/work/projects` returns 201.
- `POST /api/work/missions` returns 201.
- `POST /api/work/missions/{id}/start` returns Mission detail.
- `GET /api/work/missions/{id}/events` returns events.

### Step 7: Mount Routes

Update `backend/main.py`.

Acceptance:

- Existing app imports.
- Existing tests still pass.
- Existing `/api/tasks` remains mounted.

### Step 8: Frontend API Client

Add `frontend/src/api/workMode.js`.

Acceptance:

- All functions call expected paths.
- `npm run build` still passes.

### Step 9: Frontend Work Console

Replace or extend WorkPage to use Mission Runtime.

Minimum UI:

- Project create form.
- Mission create form.
- Mission list.
- Start/Stop button.
- Timeline.
- Product panel.
- Warnings.
- Raw logs.

Acceptance:

- No text overflow on desktop or mobile.
- Copy is short.
- `npm run build` passes.

### Step 10: Local Verification

Backend:

```bash
cd backend
python -m unittest discover -s work_mode/tests -p 'test*.py'
python -m unittest discover -s . -p 'test*.py'
```

If root discovery finds zero tests, run each module test directory explicitly and document the limitation.

Frontend:

```bash
cd frontend
npm run build
```

### Step 11: Target-Machine Smoke

Do not stop existing services.

Use a new free port.

Recommended pattern:

```bash
cd ~/hackson_backend_test/backend
HACKSON_MONGO_DATABASE=hackson_work_mode_smoke \
HACKSON_JWT_SECRET=target-test-secret-with-more-than-32-bytes \
PYTHONPATH=. \
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port <new_port>
```

Smoke:

- `GET /health`
- register user
- create Project
- create Mission
- start Mission
- poll events
- stop Mission if still running

Only update `api.md` after this target smoke passes.

## 11. Testing Matrix

### V0 Stabilization Batch

Scope for the current batch:

- Keep the worker deterministic.
- Do not add model planning.
- Do not add separate Work-only Employees.
- Verify the existing Mission state machine.

Required stable behaviors:

- Starting a draft Mission writes `MISSION_STARTED` and creates one running Run.
- Completed worker runs end with `MISSION_COMPLETED`.
- Stop on a draft Mission returns `409`.
- Stop on a running Mission writes `MISSION_STOP_REQUESTED`.
- A worker that observes `stopping` writes `MISSION_STOPPED` and leaves the Mission terminal.
- Event polling with `afterSequence` returns only later events.
- The Work UI keeps Mission list status synchronized with Mission detail status.

Backend unit:

- Schema validation.
- Service state transitions.
- Event sequencing.
- Worker terminal states.
- Ownership checks.

Backend route:

- Auth required.
- Happy path.
- Not found.
- Invalid transition.

Frontend build:

- `npm run build`.

Frontend manual:

- Desktop screenshot.
- Mobile screenshot.
- Create Project.
- Create Mission.
- Confirm exactly two user Agents are visible.
- Confirm Mission can select one Agent as Lead.
- Start Mission.
- See timeline update.
- See product panel.
- Stop running Mission.

Target smoke:

- New port only.
- New database only unless intentionally using production database smoke.
- No service stops.

## 12. Migration Strategy

## 13. V0.1 Employee Library Implementation Plan

### 13.1 Goal

Status: superseded for the current product UI by Section 15, but retained as legacy API history.

Implement the smallest product-grade Employee loop from `brainstorm2.md`:

```text
Create Employee
  -> Add Employee to Project team
  -> Create Mission with that Employee as Lead
  -> Start Mission
  -> Mission UI and event payload show selected Lead
```

### 13.2 Product Rules

- Employee personality and permissions are separate.
- V0.1 stores permissions but does not execute tools from them.
- Project team membership controls which Employees can be selected as Mission Lead.
- Default `Lead` remains available for existing Projects and old Missions.
- Do not implement brainstorm, Codex delegation, reviewer loop, or employee memory growth in V0.1.

### 13.3 Backend Additions

Collections:

- `work_employees`
- `work_project_employees`

Employee fields:

- `name`
- `role`
- `personality`
- `experience`
- `skills`
- `permissions`
- `default_output_style`
- `status`

Project membership fields:

- `project_id`
- `employee_id`
- `role_on_project`
- `is_lead_default`

Routes:

- `POST /api/work/employees`
- `GET /api/work/employees`
- `POST /api/work/projects/{projectId}/employees`
- `GET /api/work/projects/{projectId}/employees`

Mission creation:

- If `leadEmployeeId` is `employee_default_lead`, use the default Lead.
- Otherwise require that the Employee belongs to the same Project team.
- Persist `lead_employee_name` from the Employee profile.
- Event payload must include selected Employee.

### 13.4 Frontend Additions

Work page left rail:

- Compact Employee create form.
- Team list for selected Project.
- Add Employee to Project.
- Mission create form includes Lead selector.

Inspector:

- Show selected Lead.
- Show Project Team count.

Copy must stay short:

- `Employees`
- `Team`
- `Lead`
- `Role`
- `Add`

### 13.5 Verification

Local:

- `python -m unittest discover -s work_mode/tests -p 'test*.py'`
- `npm run build`

Target:

- New target-machine port only.
- New MongoDB database.
- Verify Employee API.
- Verify Project Team API.
- Verify Mission created with selected Lead.
- Verify Mission events contain selected Lead.
- Browser screenshot desktop and mobile.

V0 can coexist with old Work tasks.

During V0:

- Keep `/api/tasks`.
- Add `/api/work`.
- Frontend Work page can switch to Mission Runtime when `/api/work` is verified.
- Do not delete `backend/tasks/` until `/api/work` has target-machine verification and the product decision is recorded.

Later:

- Either migrate old tasks into Missions.
- Or keep old tasks as archived v1.5 data.

## 14. V0.1.1 Workspace UI Cleanup Plan

### 14.1 Goal

Fix the current Work UI density problem.

The first Work screen must be a simple Workspace:

```text
Workspace
  -> Existing Projects
  -> New Project
```

Historical V0.1.1 Project detail could show:

```text
Project
  -> Employees
  -> Team
  -> Missions
  -> Mission Console
  -> Inspector
```

Current V0.1.2 Project detail replaces Employees and Team with the two user-owned Agents from `Me`.

### 14.2 Product Rules

- Do not auto-select the first Project on Work load.
- Do not show Employee controls on the Workspace screen.
- Do not show legacy Employee or Team controls in the current V0.1.2 Project detail.
- Do not show Mission controls on the Workspace screen.
- Do not show raw logs or Inspector on the Workspace screen.
- Project cards must be directly clickable.
- New Project must persist through the target-machine API before opening Project detail.
- Project detail must have a clear Back to Workspace action.
- New Project must not ask the user for `repoPath`.
- `repoPath` is an internal runtime field for later worker execution, not a Workspace creation field.

### 14.3 Frontend Files

Update:

- `frontend/src/features/work/WorkPage.jsx`
- `frontend/src/features/work/components/ProjectMissionRail.jsx`
- `frontend/src/features/work/components/README.md`
- `frontend/src/styles.css`

Add:

- `frontend/src/features/work/components/WorkspaceView.jsx`

### 14.4 Implementation Steps

1. Add `WorkspaceView.jsx`.
2. Change initial load in `WorkPage.jsx` to load Projects only.
3. Add `openProject(project)` helper that loads Missions, selected Mission, and events.
4. Add `backToWorkspace()` helper that clears selected Project, selected Mission, Missions, and events from the visible UI.
5. Move Project create controls from `ProjectMissionRail` into `WorkspaceView`.
6. Keep Agent selection, Mission create, and Mission list inside `ProjectMissionRail`.
7. Add a Back button and selected Project header to `ProjectMissionRail`.
8. Add responsive Workspace styles.
9. Hide `repoPath` from Workspace and Project detail UI.
10. Make backend Project creation accept name-only payloads.

### 14.5 Verification

Local:

- `npm run build`

Target-backed browser:

- Use the latest verified Work Mode target tunnel.
- Use Vite dev server with proxy to the tunnel.
- Login with a target-machine user that already has Projects.
- Verify Workspace shows existing Projects and New Project only.
- Open a Project and verify Project detail shows the two Agents, Missions, Console, Inspector.
- Create a Project with name only and verify it appears through the target-backed API.
- Capture desktop and mobile screenshots.

No `api.md` route changes are required unless a new API is added or a verified port record changes.

## 15. V0.1.2 Two Agent Mission Lead Plan

### 15.1 Goal

Fix the current product confusion.

The user has exactly two editable Agents from `Me`. Work Project detail must not ask the user to create Employees or build a Team. A Project opens to two Agent choices, a Mission form, and the Mission console.

The user flow must be:

```text
Work
  -> New Project or open Project
  -> choose agent_1 or agent_2 as Lead
  -> fill Mission and Goal
  -> Create
  -> Start
```

### 15.2 Backend Rules

- `POST /api/work/missions` accepts `leadEmployeeId: "agent_1"` and `leadEmployeeId: "agent_2"`.
- The route resolves Agent profiles from the authenticated user.
- Mission storage keeps the Agent slot in `lead_employee_id`.
- Mission storage keeps the user-edited Agent name in `lead_employee_name`.
- Mission storage keeps the user-edited Agent voice in `lead_employee_role` for the existing response shape.
- Event payload keeps the compatibility key `employee`, but the value represents the selected user Agent.
- Legacy Employee routes stay available for old tests and old data, but the current frontend does not call them.

### 15.3 Frontend Rules

Update:

- `frontend/src/features/work/WorkPage.jsx`
- `frontend/src/features/work/components/ProjectMissionRail.jsx`
- `frontend/src/features/work/components/InspectorPanel.jsx`
- `frontend/src/features/work/components/MissionHeader.jsx`
- `frontend/src/features/work/components/README.md`
- `frontend/src/features/work/README.md`
- `frontend/src/styles.css`

Rules:

- `WorkPage` receives `agents` from `App.jsx`.
- Normalize and render exactly two user-owned Agents.
- Do not call `listEmployees`, `createEmployee`, `addProjectEmployee`, or `listProjectEmployees` from the current Work UI.
- Project detail left rail shows `Agents` and `Missions`.
- Mission form uses Agent options for `Lead`.
- The create button says `Create`, not `Add`.
- Inspector label says `Agents`, not `Team`.
- When no Mission exists, center header says `Create mission` and Start stays disabled.

### 15.4 Regression Tests

Backend:

- Service test: `agent_1` can lead a Mission without Employee or Team setup.
- Route test: route resolves edited user Agent profiles and stores the edited Agent name.
- Existing legacy Employee tests continue passing.

Frontend:

- Build passes.
- Target-backed browser screenshot shows no Employee create form.
- Target-backed browser screenshot shows exactly two Agents from the current user profile.
- Creating a Mission enables Start.

### 15.5 Target Smoke

Use a new target-machine port and a new MongoDB database.

Smoke sequence:

1. Register or log in a target-machine test user.
2. Update `agentProfiles` with two distinct names.
3. Create Project with name only.
4. Create Mission with `leadEmployeeId: "agent_1"`.
5. Assert Mission response has `leadEmployeeId: "agent_1"`.
6. Assert Mission response and first event have the edited Agent name.
7. Start Mission.
8. Poll events until terminal or until `MISSION_STARTED` is visible.
9. Open frontend against the same target backend.
10. Capture desktop and mobile screenshots.

Only after this passes, update `api.md`.

## 16. Done Definition

V0 is done only when:

- `docs/work_mode/versions.md` and `plan.md` match implementation.
- Backend exposes verified `/api/work` routes.
- Frontend renders Mission console.
- A Mission can be created, started, and completed.
- Events are persisted and visible.
- User can stop a running Mission.
- Existing Auth, Idle, Chat, Me, and `/api/tasks` are not broken.
- Local tests pass.
- Frontend build passes.
- Target-machine smoke passes on a new port.
- `api.md` is updated with only verified API details.

## 17. First Engineering Slice

Start with this exact slice:

1. Backend schemas.
2. Backend in-memory service tests.
3. Mongo repository.
4. Routes.
5. Deterministic worker.
6. Frontend API client.
7. WorkPage Mission console.
8. Local verification.
9. Target smoke.
10. `api.md` update.

Do not start with Codex CLI.

Codex CLI belongs in V0.5 after Mission events, worker lifecycle, and UI rendering are proven.
