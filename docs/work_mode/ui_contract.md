## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Work Mode UI Contract

## 1. Purpose

This document defines how the React Work UI renders V1.0 Mission Runtime state.

The model never renders UI. The UI renders persisted backend events, Products, Artifacts, and Work Windows.

## 2. Required V1.0 Surfaces

V1.0 UI MUST contain:

- Mission Timeline.
- Work Windows.
- Product Panel.
- Control Panel.

These can be arranged in the existing Work page layout, but the four surfaces must be present.

## 3. Mission Timeline

Timeline shows the process.

It MUST render:

- Lead plan updates.
- Tool calls.
- Product updates.
- Product inspections.
- Delegate window opened/completed/blocked.
- User input requested/received.
- Retryable pauses.
- Terminal status.

Large text timeline entries MUST be collapsed by default.

Timeline entries MAY show:

- Tool name.
- Agent name.
- Short reason.
- Status.
- Product or Artifact refs.
- Excerpt.

Timeline entries MUST NOT require parsing raw model prose to determine type.

## 4. Work Windows

Every `delegate_agent` call MUST create a visible Work Window.

Window card MUST show:

- Window title.
- Source Lead action.
- Delegate Agent name and slot.
- Brief.
- Status.
- Result Artifact id/title.
- Summary.
- Expand/collapse control.

Window details MAY show:

- Full brief.
- Delegate result content excerpt.
- Link to Product/Artifact panel for full result.

V1.0 Work Windows run sequentially, but UI should not assume future windows cannot run in parallel.

## 5. Product Panel

Product Panel is the canonical full-content surface.

It MUST show:

- Product list.
- Product status.
- Artifact lineage.
- Source Agent.
- Source Work Window when applicable.
- Final Product highlight.
- Full Artifact content reader.

Product Panel MUST NOT rely on Timeline payloads as the source of truth for full content.

## 6. Control Panel

Control Panel MUST show:

- Start.
- Stop.
- Resume when `paused_retryable`.
- Answer form when `waiting_input`.
- Current status.
- Budget summary.

V1.0 text-only `waiting_input` MAY auto-resume after user answer, but UI still MUST show the question and answer.

## 7. Collapsed Content Rules

Collapsed by default:

- `work_product` large content.
- `inspect_product` inspected excerpts.
- Delegate window result content.
- Long error payloads.

Expanded content MUST enforce display limits.

If content exceeds display limit, UI MUST link to the Product/Artifact reader.

## 8. Event Mapping

| Event Type | UI Surface | Default Display |
| --- | --- | --- |
| `MISSION_PLAN_UPDATED` | Timeline | Expanded summary, steps visible |
| `MODEL_TURN_STARTED` | Timeline + Control Panel | Compact active row |
| `MODEL_TURN_HEARTBEAT` | Timeline + Control Panel | Compact active row |
| `MODEL_TURN_COMPLETED` | Timeline | Compact completed row |
| `MODEL_TURN_RETRYING` | Timeline + Control Panel | Retry visible |
| `TOOL_CALLED` | Timeline | Collapsed reason and tool |
| `PRODUCT_UPDATED` | Timeline + Product Panel | Timeline collapsed, Product full |
| `PRODUCT_INSPECTED` | Timeline | Collapsed, expandable inspected excerpt |
| `WORK_WINDOW_OPENED` | Timeline + Work Windows | Window card created |
| `WORK_WINDOW_COMPLETED` | Timeline + Work Windows + Product Panel | Result linked |
| `WORK_WINDOW_BLOCKED` | Timeline + Work Windows | Block reason visible |
| `WORK_WINDOW_FAILED` | Timeline + Work Windows | Failed window visible |
| `USER_INPUT_REQUESTED` | Timeline + Control Panel | Question visible |
| `MISSION_PAUSED_RETRYABLE` | Timeline + Control Panel | Resume visible |
| `MISSION_COMPLETED` | Timeline + Product Panel | Final Product highlighted |
| `MISSION_BLOCKED` | Timeline + Control Panel | Block reason visible |
| `MISSION_FAILED` | Timeline + Control Panel | Error visible |

## 9. Copy Rules

Frontend copy MUST stay short.

Recommended labels:

- `Plan`
- `Windows`
- `Product`
- `Resume`
- `Answer`
- `Final`
- `Blocked`
- `Failed`

Avoid long explanatory UI text. The process itself should be visible through cards and events.

## 10. Browser Verification

V1.0 browser smoke MUST verify:

- Mission can start.
- Timeline shows plan and tool events.
- At least two delegate windows are visible.
- Delegate windows are collapsed by default and expandable.
- Product Panel shows final Product full content.
- Completed Mission highlights final Product.
- No large text overlaps controls.
- Mobile layout keeps Product readable.

## 11. 代办

- Finalize component split after backend response shapes are implemented.
