## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 3: Delegate Window Visibility

## Problem

Delegate Agent work is part of the product value. If delegate calls are hidden observations, Work Mode loses the visible multi-window process the user expects.

## Decision

Every `delegate_agent` call MUST create a visible Work Window.

V1.0 windows execute sequentially. Parallel execution is V1.3.

## Risks

- Too many windows can clutter UI.
- Delegate output can duplicate Product content.
- Window status can drift from Artifact status.

## Constraints

- Work Window MUST have id, title, brief, agent slot, status, result Artifact id, and summary.
- Work Window MUST be collapsed by default when content is large.
- Work Window MUST be expandable.
- Delegate output MUST persist as an Artifact.
- Artifact MUST reference `workWindowId` and `sourceAgentId`.
- Delegate windows MUST NOT finish Mission.
- Delegate windows MUST NOT recursively delegate in V1.0.

## UI Rule

Timeline shows the window event. Work Window panel shows the process. Product panel shows the full result content.

## Acceptance

- Full smoke shows at least two delegate windows.
- Each window can be expanded.
- Each window links to an Artifact.
- Final Product can reference delegate Artifacts.
