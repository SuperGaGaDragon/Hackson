## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Work Mode UI Contract

## 1. Purpose

This document defines how the React Work UI renders V1.0 Mission Runtime state.

The model never renders UI. The UI renders persisted backend events, Products, Artifacts, and Work Windows.

## 2. Required V1.0 Surfaces

V1.0 UI MUST contain:

- Current Activity.
- Work Windows.
- Product Panel.
- Mission Progress.
- Diagnostics.
- Control Panel.

The main Mission Console MUST render in this order:

1. Current Activity.
2. Work Windows.
3. Product Panel.
4. Mission Progress.
5. Diagnostics.

The side rail MAY render Inspector, warnings, and budget details.

## 3. Current Activity

Current Activity shows the latest safe runtime state.

It MUST render:

- Latest model state, tool action, retry, pause, completion, or failure.
- Local clock time when available.
- Short status detail.

It MUST NOT render raw chain-of-thought.

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

Work Windows MUST appear above Mission Progress.

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

Product Panel MUST NOT show only the latest Artifact as if it were the whole deliverable.

If a final Product exists, Product Panel MUST default to an all-Artifact reader stack. The final Artifact should be visible inside that stack, and the user must be able to isolate a single Artifact from the lineage controls. If no final Product exists, Product Panel MUST keep all Product Artifacts visible in order so partially completed long-form output does not appear lost.

Artifact navigation MUST keep a stable scan rhythm. Desktop SHOULD render a fixed-width Artifact Navigator beside the reader instead of a wrapping card grid. Navigator rows SHOULD clamp generated titles, expose short type labels, and avoid letting title length resize the Product Panel. Mobile MAY stack the navigator above the reader.

## 6. Mission Progress

Timeline shows the process.

It MUST render:

- Lead plan updates.
- Tool calls.
- Product updates.
- Product inspections.
- Web Search completed/failed events.
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

Timeline rows MUST show local clock time when `createdAt` exists. Sequence number MAY appear as muted diagnostic metadata.

Repeated heartbeat events MUST render compactly and MUST NOT dominate the Mission Console.

Progress row expansion:

- Rows expand inline, not as raw log modals.
- One expanded row at a time is preferred.
- Expanded details MUST be bounded and structured.
- Plan rows show plan steps.
- Product rows show Product id, Artifact id, kind, summary, bounded excerpt, and Product link.
- Window rows show brief, expected output, target Product, source Artifacts, result summary, and linked Artifact.
- Review rows show verdict, score, findings summary, and Review Artifact link.
- Discussion rows show participants, linked Product/Artifact/Window, transcript summary, recommendation, and Discussion Artifact link.
- Web Search rows show query, source count, source links, provider, and truncation state.
- Full long-form Product content MUST remain in Product Panel.

## 7. Diagnostics

Diagnostics is the engineering/debug surface.

It MUST be collapsed by default.

It SHOULD show:

- Event sequence.
- Event type.
- Local clock time.
- Payload JSON.

Diagnostics MUST NOT be named `Logs` in the main UI.

## 8. Control Panel

Control Panel MUST show:

- Start.
- Stop.
- Resume when `paused_retryable`.
- Answer form when `waiting_input`.
- Current status.
- Budget summary.

V1.0 text-only `waiting_input` MAY auto-resume after user answer, but UI still MUST show the question and answer.

## 8.1 Project Rail And Mission Creation

Selected Project rail default content:

- Project name.
- Back/navigation command.
- Agent list.
- Mission list.
- `New Mission` command.

Mission creation form:

- MUST NOT stay permanently visible after a Mission is selected.
- MUST open from `New Mission` as a modal or drawer.
- MUST close after successful Mission creation.
- SHOULD preserve typed values if the modal/drawer is dismissed accidentally without creation.

Completed or running Mission view SHOULD prioritize reading and process context over creating another Mission.

## 9. Collapsed Content Rules

Collapsed by default:

- `work_product` large content.
- `inspect_product` inspected excerpts.
- `web_search` result snippets beyond the first few sources.
- Delegate window result content.
- Long error payloads.

Expanded content MUST enforce display limits.

If content exceeds display limit, UI MUST link to the Product/Artifact reader.

## 10. Event Mapping

| Event Type | UI Surface | Default Display |
| --- | --- | --- |
| `MISSION_PLAN_UPDATED` | Progress | Expanded summary, steps visible |
| `MODEL_TURN_STARTED` | Activity + Progress | Compact active row |
| `MODEL_TURN_HEARTBEAT` | Activity + Progress | Compact active row |
| `MODEL_TURN_COMPLETED` | Progress | Compact completed row |
| `MODEL_TURN_RETRYING` | Activity + Progress + Control Panel | Retry visible |
| `TOOL_CALLED` | Activity + Progress | Decision/action row |
| `PRODUCT_UPDATED` | Progress + Product Panel | Progress compact, Product full |
| `PRODUCT_INSPECTED` | Progress | Collapsed inspected excerpt |
| `PRODUCT_REVIEWED` | Progress + Product Panel | Review summary, Artifact linked |
| `WEB_SEARCH_COMPLETED` | Progress + Diagnostics | Query, result count, source links |
| `WEB_SEARCH_FAILED` | Activity + Progress + Diagnostics | Search error and retryability |
| `WORK_WINDOW_OPENED` | Progress + Work Windows | Window row created |
| `WORK_WINDOW_COMPLETED` | Progress + Work Windows + Product Panel | Result linked |
| `WORK_WINDOW_BLOCKED` | Progress + Work Windows | Block reason visible |
| `WORK_WINDOW_FAILED` | Activity + Progress + Work Windows | Failed window visible |
| `DISCUSSION_WINDOW_OPENED` | Progress + Work Windows | Discussion row created |
| `DISCUSSION_WINDOW_COMPLETED` | Progress + Work Windows + Product Panel | Transcript summary linked |
| `DISCUSSION_WINDOW_BLOCKED` | Progress + Work Windows | Block reason visible |
| `DISCUSSION_WINDOW_FAILED` | Activity + Progress + Work Windows | Failed discussion visible |
| `USER_INPUT_REQUESTED` | Progress + Control Panel | Question visible |
| `MISSION_PAUSED_RETRYABLE` | Activity + Progress + Control Panel | Resume visible |
| `MISSION_COMPLETED` | Activity + Progress + Product Panel | Final Product highlighted |
| `MISSION_BLOCKED` | Activity + Progress + Control Panel | Block reason visible |
| `MISSION_FAILED` | Activity + Progress + Control Panel | Error visible |
| `RAW_LOG` | Diagnostics | Collapsed raw detail |

## 11. Copy Rules

Frontend copy MUST stay short.

Recommended labels:

- `Plan`
- `Windows`
- `Product`
- `Progress`
- `Diagnostics`
- `Resume`
- `Answer`
- `Final`
- `Blocked`
- `Failed`

Avoid long explanatory UI text. The process itself should be visible through cards and events.

## 12. Browser Verification

V1.0 browser smoke MUST verify:

- Mission can start.
- Timeline shows plan and tool events.
- At least two delegate windows are visible.
- Work Windows render above Progress.
- Delegate windows are collapsed by default and expandable.
- Product Panel shows Product list and Artifact lineage.
- Product Panel shows final Product full content.
- Progress plan rows can expand to show steps.
- Progress Product rows can expand to show bounded detail without rendering full long-form content.
- Progress Web Search rows can expand to show bounded source links and snippets.
- Selected Project rail hides the Mission creation form until `New Mission` is used.
- Diagnostics is present and collapsed by default.
- Completed Mission highlights final Product.
- No large text overlaps controls.
- Mobile layout keeps Product readable.

## 13. 代办

- Add streaming activity when V1.2 backend stream is available.
