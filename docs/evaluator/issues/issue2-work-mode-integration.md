## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 2: Work Mode Integration

## Problem

AgentLens could be built as a separate product surface with its own task runner, trace store, dashboard, and report database.

That would be conceptually clean for a standalone company pitch, but inside Hackson it would duplicate Work Mode concepts that already exist:

- Mission.
- Run.
- Event.
- Product.
- Artifact.
- Work Window.
- Tool protocol.
- Progress UI.

Duplication would slow the hackathon build and split the product story.

## Decision

Evaluator Runtime starts as a Work Mode reliability layer.

It reads Work Mode state and writes Reliability Reports back into Work Mode as report Artifacts and report events.

## Self-Grilled Decisions

### Is this too coupled to Work Mode?

For V1.0, no.

The first supported scope is Research Missions, and Research Missions already need Work Mode trace and `web_search`. A separate evaluator app can come later only after the report contract proves itself.

### Should Evaluator Runtime live in `backend/work_mode/` or a new `backend/evaluator/`?

Recommendation:

- Start implementation in `backend/work_mode/` because it needs WorkModeService and existing repository primitives.
- Keep class names and docs clean enough that `backend/evaluator/` can be extracted later.

### Should reports be stored in dedicated collections immediately?

No for V1.0.

Persist report payloads as immutable report Artifacts and `RELIABILITY_REPORTED` events first. Add dedicated collections when report history, filtering, or project-level analytics require them.

## Consequences

- Faster MVP.
- Clearer demo.
- Less duplicate schema.
- Future extraction remains possible if report contracts stay explicit.

## Acceptance

- Work Console can show a Reliability Report without a separate app route.
- Existing Work Mode Mission detail remains the main read API.
- Report persistence does not overwrite Product content.
