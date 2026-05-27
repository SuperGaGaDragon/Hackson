## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

# Work Mode Version Roadmap

## 1. Product North Star

Work Mode is an Agent Mission Runtime that uses the two user-owned Agents edited in `Me`.

The user creates Projects. Each Project can contain multiple Missions. Each Mission chooses one Lead Agent from the two account Agent profiles (`agent_1`, `agent_2`). The user edits those Agents once in `Me`, then reuses them inside every Project.

A Mission runs a supervised loop that uses fixed UI events to show progress and controlled worker execution to change code, run commands, collect diffs, run tests, request approval, and produce a final result.

The model does not draw UI. The model emits structured events and tool decisions. The frontend renders those events with fixed React surfaces. The backend owns the runtime loop, safety gates, persistence, and worker execution.

The Lead Agent is the mission driver. The Lead Agent can use three tool classes:

- UI tools: emit React-rendered mission events.
- Execution tools: invoke shell, Codex CLI, tests, and file-system work through backend safety gates.
- Agent tools: ask the other user Agent to brainstorm, critique, summarize, or review.

## 2. Version Principles

- Each version must ship a complete vertical slice.
- Each version must preserve the current production Idle, Chat, Auth, Me, and minimal Work flows unless explicitly replaced.
- Each version must be verifiable on the target machine without stopping existing services.
- Each version must separate Work Mode memory and logs from Idle and Companion defaults.
- Each version must treat Codex and shell execution as controlled worker actions, not direct model freedom.
- Each version must record events before showing them in UI.
- Each version that uses Agents must persist which Agent made or influenced an event.
- Agent personality and experience are user-editable product data, but Mission execution still runs under backend safety gates.
- The current product UI must not ask the user to create a separate Employee or Project Team before starting a Mission.

## 3. Version Summary

| Version | Name | Product result | Runtime result | Release gate |
| --- | --- | --- | --- | --- |
| V0 | Mission Event Console | User can create a Project and Mission, start/stop it, and watch live structured events. | No autonomous code edits required. Worker can run a safe stub or read-only command. | Event stream works end to end on target machine. |
| V0.1 | Legacy Employee Library | Legacy API can create Employees, add them to a Project team, and choose a Lead Employee for a Mission. | Mission state stores the selected Lead Employee and events show that Employee. | Historical target smoke proved one user-created Employee can lead a Mission. Current UI no longer uses this flow. |
| V0.1.1 | Workspace UI Cleanup | Work opens to a simple Workspace: existing Projects and New Project. | Mission and console controls are only visible inside a selected Project. | Target-backed browser smoke proves Projects persist on target MongoDB and Project detail opens cleanly. |
| V0.1.2 | Two Agent Mission Lead | Project detail shows the two user-edited Agents and lets the user choose one as Mission lead. | Mission creation accepts `agent_1` or `agent_2` directly from the authenticated user's Agent profiles. | Target smoke proves `leadEmployeeId: agent_1` works without Employee or Team setup, and browser screenshot shows no Employee create form. |
| V0.5 | Single Codex Run | User can run one controlled Codex step for a Mission and see logs, summary, and artifacts. | One worker process invokes Codex or a configured command once. | Logs and result artifacts are persisted and visible. |
| V1 | Supervised Mission Loop | Mission repeats controlled iterations until done, stopped, blocked, or limit reached. | Hard-coded supervisor loop controls max iterations, runtime, no-progress, and approval gates. | A coding Mission can run multiple iterations and stop deterministically. |
| V1.25 | Project Employee Roster | User can add Employees to a Project, edit personality and experience, and choose a Lead Employee for a Mission. | Mission state stores roster selection and lead employee. | A Mission displays which Employee is leading and which Employees are available. |
| V1.5 | Diff, Tests, Approval | User sees changed files, test results, warnings, and approval cards. | Worker captures diff, command results, and approval-required states. | Dangerous actions block until user approval. |
| V2 | Lead + Supporting Employees | Lead Employee can ask other Employees to brainstorm, critique, summarize, or review. | Employee tool calls produce structured events and raw conversation records. | A Mission shows brainstorm process without flooding the main timeline. |
| V3 | Multi Project Runtime | Multiple Projects and Missions can run or pause independently. | Runtime isolates repo paths, worktrees, events, and workers per Mission. | Two Missions can run without log, state, or repo collision. |
| V4 | Custom Agent Graph | Advanced users define role graphs and mission policies. | Runtime executes configured role graph under the same safety and event protocol. | Custom graph cannot bypass safety gates. |

## 4. V0 Mission Event Console

### Product Goal

Give the user a real Mission page instead of a chat page.

The first screen must show:

- Project list.
- Mission list.
- Mission header.
- Progress timeline.
- Summary cards.
- Warning cards.
- Product panel.
- Raw log panel.
- Start and Stop controls.

### Runtime Scope

V0 does not need real Codex edits.

V0 must prove:

- Mission state can be persisted.
- Mission events can be persisted.
- A worker can append events asynchronously.
- The frontend can stream or poll events.
- The user can stop a running Mission.
- Existing production app remains stable.

### Data Scope

Required collections:

- `work_projects`
- `work_missions`
- `work_runs`
- `work_steps`
- `work_events`

Optional in V0:

- `work_artifacts`
- `work_approvals`
- `work_employees`
- `work_project_employees`

### Required Event Types

- `MISSION_CREATED`
- `MISSION_STARTED`
- `STEP_STARTED`
- `SUMMARY`
- `WARNING`
- `RAW_LOG`
- `PRODUCT_UPDATED`
- `STEP_COMPLETED`
- `MISSION_STOP_REQUESTED`
- `MISSION_COMPLETED`
- `MISSION_FAILED`

### Non Goals

- No multi-agent reviewer.
- No editable Employee roster.
- No arbitrary shell command UI.
- No Git push.
- No deploy.
- No persistent autonomous background daemon beyond the controlled worker loop needed for V0.

## 5. V0.5 Single Codex Run

## 5. V0.1 Employee Library

### Product Goal

Status: legacy API history. V0.1.2 replaced this as the current product UI because the account already owns exactly two editable Agents from `Me`.

Convert Work Mode language from generic Agents to a project team.

The user can:

- Create an Employee profile.
- Add that Employee to a Project team.
- Choose the Employee as Mission Lead.
- See the Lead Employee on the Mission page and in Mission events.

### Runtime Scope

V0.1 only persists Employee profiles and membership.

Do not implement:

- Employee-to-Employee brainstorm.
- Codex delegation.
- Reviewer loop.
- Employee memory growth.
- Permission-enforced tool execution.

### Release Gate

Target-machine smoke must verify:

- `POST /api/work/employees`
- `GET /api/work/employees`
- `POST /api/work/projects/{projectId}/employees`
- `GET /api/work/projects/{projectId}/employees`
- `POST /api/work/missions` with `leadEmployeeId`
- Mission event payload includes the selected Employee.

## 5.1 V0.1.1 Workspace UI Cleanup

### Product Goal

Make Work Mode feel like a product workspace instead of a dense control panel.

The Work entry screen must show only:

- Existing Projects.
- New Project.

Historical V0.1.1 context: the user had to open a Project before seeing:

- Employees.
- Project Team.
- Missions.
- Mission console.
- Inspector.

Current V0.1.2 UI replaces Employees and Project Team with the two user-owned Agents.

### Runtime Scope

This is a small product cleanup on top of verified V0.1 APIs. The frontend hides `repoPath`, and the backend accepts Project creation with `name` only while returning an empty `repoPath` for compatibility.

No route or worker behavior changes are required.

### Release Gate

Target-backed smoke must verify:

- Backend is the target-machine port `8143`.
- MongoDB database is `hackson_work_mode_v01_employees`.
- Existing Projects render on the Workspace screen.
- New Project creates a real Project with name only and opens Project detail.
- `POST /api/work/projects` accepts `{ "name": "novel" }` without `repoPath`.
- Historical V0.1.1 Project detail showed Team, Employees, Missions, and Mission console.
- Current V0.1.2 Project detail shows Agents, Missions, and Mission console.
- Workspace screen does not show Mission or Employee controls before a Project is opened.
- Workspace screen does not expose `repoPath`.

## 5.2 V0.1.2 Two Agent Mission Lead

### Product Goal

Remove the confusing Employee and Project Team setup from the current Work UI.

The current user has exactly two editable Agents from `Me`. A Project does not create new employees. A Mission selects one of those two Agents as the Lead Agent, then the user clicks Start after the Mission exists.

### User Flow

1. Open Work.
2. Create or select a Project.
3. Project detail shows the two Agents from `Me`.
4. Choose one Agent as Lead.
5. Fill Mission and Goal.
6. Click Create.
7. Click Start.

### Runtime Scope

- Keep legacy Employee APIs for backward compatibility.
- `POST /api/work/missions` must accept `leadEmployeeId` values `agent_1` and `agent_2`.
- Mission records must store the selected Agent slot, user-edited Agent name, and user-edited Agent voice.
- Mission events must include the selected Agent in `payload.employee` for compatibility with existing event cards.

### Release Gate

Target-machine smoke must verify:

- Backend is on a new target-machine port.
- MongoDB uses a new smoke database.
- `POST /api/work/missions` accepts `leadEmployeeId: "agent_1"` without any Employee or Team API call.
- Mission response and first event show the user-edited Agent name.
- Project detail does not show Employee creation, Project Team add, or `Name` / `Role` Employee inputs.
- Browser screenshot proves the user can understand the sequence: choose Agent, create Mission, then Start.

## 6. V0.5 Single Codex Run

### Product Goal

Let the user start one Mission that invokes a controlled code worker once and returns visible logs and result state.

### Runtime Scope

The worker performs one action:

1. Prepare Mission execution context.
2. Create or select a safe work directory.
3. Run Codex CLI or a configured V0 runner.
4. Capture stdout and stderr.
5. Capture changed files and diff when available.
6. Save artifacts.
7. Emit summary, warning, or product events.
8. Mark step complete or failed.

### Release Gate

Target-machine smoke must verify:

- `POST /api/work/projects`
- `POST /api/work/missions`
- `POST /api/work/missions/{missionId}/start`
- `GET /api/work/missions/{missionId}/events`
- Worker emits at least one `RAW_LOG` and one terminal Mission event.

## 7. V1 Supervised Mission Loop

### Product Goal

The user starts a Mission once. The system continues step by step until a stop condition fires.

### Stop Conditions

- User stops the Mission.
- Agent declares complete and supervisor accepts.
- Max iterations reached.
- Max runtime reached.
- No progress for configured limit.
- Worker fails too many times.
- Approval is required.
- Mission is blocked.

### Runtime Rule

The model may request `loop.continue`, but the supervisor decides whether to continue.

The supervisor must be deterministic. It uses persisted Mission state, run state, safety policy, iteration counters, timestamps, and approval status.

## 8. V1.5 Diff, Tests, Approval

### Product Goal

Make the Mission page useful for real code review.

The user must see:

- Changed files.
- Diff summary.
- Test command.
- Test result.
- Failure reason.
- Approval card for risky actions.

### Approval Gates

Require approval before:

- Deleting files outside the Mission worktree.
- Running migrations.
- Installing new system packages.
- Touching production env files.
- Pushing to remote.
- Deploying.
- Running commands outside the allowlist.

## 9. V1.25 Project Employee Roster

### Product Goal

Let users staff a Project with AI Employees.

Each Employee can have:

- Name.
- Role.
- Personality.
- Working style.
- Experience notes.
- Avatar or display color.
- Project-specific memory notes.

Each Mission can select:

- Lead Employee.
- Supporting Employees.

### Runtime Scope

V1.25 does not need multi-Employee execution yet.

It must persist roster data and show which Employee is responsible for the Mission.

### Release Gate

- User can create an Employee.
- User can add Employee to a Project.
- User can choose a Lead Employee when creating a Mission.
- Mission events show the Lead Employee.

## 10. V2 Lead + Supporting Employees

### Product Goal

Improve quality by allowing the Lead Employee to consult supporting Employees.

### Runtime Flow

1. Supervisor chooses next goal.
2. Lead Employee decides whether to act directly or ask another Employee.
3. Supporting Employee returns brainstorm, critique, summary, or review.
4. Lead Employee decides whether to call execution tools.
5. System captures diff, logs, and tests.
6. Reviewer-style Employee can evaluate artifacts.
7. Supervisor continues or stops.

### Employee Tool Calls

Required tools:

- `employee.brainstorm`
- `employee.review`
- `employee.summarize`
- `employee.challenge`

These tools write structured `EMPLOYEE_MESSAGE` or `BRAINSTORM_SUMMARY` events.

### Release Gate

A Mission can show a folded brainstorm thread and a concise Lead Employee decision in the main timeline.

## 11. V3 Multi Project Runtime

### Product Goal

Run multiple independent Projects and Missions.

### Runtime Requirements

- Project owns repo path and settings.
- Mission owns runtime policy.
- Run owns one execution attempt.
- Step owns one worker action.
- Event owns all user-visible progress.
- Worktree or branch is isolated per Mission when edits are enabled.

### Release Gate

Two Missions for two Projects can run without shared logs, shared worktrees, shared approval states, or crossed UI streams.

## 12. V4 Custom Agent Graph

### Product Goal

Let advanced users define custom role graphs.

### Required Guardrail

Custom graphs cannot bypass:

- Command allowlist.
- Forbidden command filter.
- Approval gates.
- Max runtime.
- Max iterations.
- Workspace isolation.
- Event persistence.

## 13. Current Repository Position

The repository currently has:

- Production target machine and FastAPI deployment.
- MongoDB persistence.
- Auth.
- React app shell.
- Minimal Work task and Work message APIs.
- Context isolation for `work` mode.

The repository does not yet have:

- Editable Work Mode Employees.
- Project employee roster.
- Lead Employee selection.
- Project runtime.
- Mission runtime.
- Run and Step persistence.
- Mission event protocol.
- Worker process for Codex or shell execution.
- Live Mission stream.
- Diff, test, approval, or artifact UI.

Therefore the next implementation target is V0, not V1.
