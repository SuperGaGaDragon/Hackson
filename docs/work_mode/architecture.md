## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Work Mode Architecture

## 1. Purpose

This document defines the V1.0 Pure API Text Mission Loop architecture.

It replaces the old fixed single-run Work Mode model with a model-driven Mission Runtime. The model chooses tools; the backend validates and executes them; the UI renders persisted events.

## 2. Target Shape

```text
React Work UI
  -> FastAPI Work routes
    -> WorkModeService
      -> MissionLoopRunner
        -> MissionContextBuilder
        -> ToolCallingModelClient
        -> ToolValidator
        -> ToolExecutor
          -> EventRepository
          -> ProductRepository
          -> ArtifactRepository
          -> WorkWindowRepository
```

V1.0 MAY implement Product and WorkWindow persistence inside existing Work Mode collections if that avoids unnecessary schema churn. The public architecture still treats Product, Artifact, and Work Window as distinct concepts.

## 3. Responsibility Boundaries

### 3.1 Routes

Routes MUST:

- Authenticate current user.
- Parse request payloads.
- Call `WorkModeService`.
- Return public response shapes.

Routes MUST NOT:

- Build model prompts.
- Execute model tools.
- Mutate Mission state outside service methods.

### 3.2 WorkModeService

Service MUST:

- Enforce ownership.
- Validate Mission state transitions.
- Create Project, Mission, Run, Step, Event, Product, Artifact, and Work Window records.
- Start, stop, resume, and answer waiting Missions.
- Expose public Mission detail for UI.

Service MUST NOT:

- Let the model bypass validation.
- Execute file, shell, browser, or Codex CLI tools in V1.0.

### 3.3 MissionLoopRunner

MissionLoopRunner MUST:

- Load Mission state.
- Build context for the Lead Agent.
- Ask the model for exactly one tool call.
- Reject plain assistant text.
- Validate the selected tool and arguments.
- Execute the tool.
- Persist result and observation.
- Continue until terminal state or budget limit.

MissionLoopRunner MUST NOT:

- Hard-code the order of `mission_plan`, `delegate_agent`, `work_product`, or `finish_mission`.
- Call another model turn before persisting the previous tool result.

### 3.4 ToolCallingModelClient

V1.0 uses JSON Action protocol.

The client MUST return one parsed candidate action or a parse error. Provider-native tool calling is V1.1, not V1.0.

### 3.5 ToolValidator

ToolValidator MUST:

- Check tool name is in the allowed toolbox.
- Validate arguments against the tool schema.
- Reject missing required fields.
- Reject references to Products, Artifacts, or Windows outside the current Mission.
- Enforce per-tool limits.

### 3.6 ToolExecutor

ToolExecutor MUST:

- Execute only backend-owned database actions in V1.0.
- Persist visible events for every valid tool call.
- Return a structured observation to the Lead Agent.

ToolExecutor MUST NOT:

- Execute shell commands.
- Read or write filesystem paths.
- Launch Codex CLI computer-control tools.
- Render React components from model output.

## 4. V1.0 Runtime Loop

```text
start_mission
  -> create run
  -> while budget remains:
       state = load_mission_state()
       context = build_lead_context(state)
       action = model.generate_one_action(context)
       if action invalid:
          persist format error
          retry or fail
       result = execute_tool(action)
       persist observation
       if result terminal:
          break
```

## 5. Delegate Window Flow

`delegate_agent` is a Lead Agent tool.

```text
Lead chooses delegate_agent
  -> backend creates Work Window
  -> backend calls non-lead Agent once with scoped brief
  -> delegate returns structured result
  -> backend persists delegate Artifact
  -> backend marks Work Window completed
  -> observation returns to Lead
```

Hard constraints:

- Delegate windows MUST run sequentially in V1.0.
- Delegate windows MUST NOT call tools in V1.0.
- Delegate windows MUST NOT finish the Mission.
- Delegate windows MUST be visible in UI.

## 6. Persistence Concepts

V1.0 records:

- Project: user workspace grouping.
- Mission: user goal.
- Run: one execution attempt.
- Step: coarse runtime phase.
- Event: user-visible runtime update.
- Product: logical deliverable.
- Artifact: immutable content or version under a Product.
- Work Window: one delegated Agent call.

## 7. Existing Code Mapping

Existing `backend/work_mode/` already owns:

- Projects.
- Missions.
- Runs.
- Steps.
- Events.
- Artifacts.
- Worker entrypoint.

V1.0 should extend this module instead of creating a second Work runtime.

Likely implementation additions:

- `backend/work_mode/tool_protocol.py`
- `backend/work_mode/loop.py`
- `backend/work_mode/context.py`
- `backend/work_mode/tools.py`
- `backend/work_mode/window.py`
- new tests under `backend/work_mode/tests/`

## 8. Non-Goals

V1.0 MUST NOT implement:

- Provider-native tool calling as the only path.
- Streaming UI.
- Parallel delegate windows.
- File tools.
- Shell tools.
- Codex CLI computer-control execution.
- Git mutation.
- Deploy.
- Arbitrary user command input.

## 9. 代办

- Confirm whether Product and Work Window need dedicated MongoDB collections or can start as `work_artifacts.metadata` and `work_events.payload` fields for V1.0.
