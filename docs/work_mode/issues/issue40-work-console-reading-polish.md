## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 40: Work Console Reading Polish And Warning State

## Problem

Real research/writing Missions now expose the correct underlying objects, but the presentation still leaks too much
runtime machinery into the first reading surface.

Observed issues:

- Reliability `History` shows repeated rows, raw ids, mixed timestamp formats, and cannot open an older report.
- Product `History` is clickable, but the backend Mission detail currently treats full Artifacts as the only list shape.
  Long Missions either silently lose older lineage or tempt the UI/API into preloading too much full content.
- Mission goals can become a large gray paragraph at the top of the console, especially for pasted assignment prompts.
- Artifact metadata exposes implementation words such as `revision / revision of <artifactId>`.
- Work times use browser-local formatting or raw ISO strings instead of one consistent product timezone.
- Section boundaries are functional but visually heavy; the page reads as stacked debug panels instead of a polished
  workflow document.
- Warnings are raw event filters. A transient pause, retry, or input request can stay in the right rail forever even
  after the Mission has moved on.
- User-provided long instructions are hard to scan and compete with the Product.

## Current Implementation Findings

Product History:

- `ProductPanel` renders `Artifact Navigator` buttons and the selected Artifact content.
- Therefore Product History is partially accessible today.
- Product metadata already stores an `artifactManifest` with id, kind, title, role, summary, deliverable flag, and
  created time.
- That manifest is the right Product History source for scanning.
- Result: the UI should render a complete Artifact Index from manifest metadata, then load the full Artifact only when
  the user chooses it.
- A fixed full-content window such as `200` is not a product-grade solution. It wastes payload, can still truncate, and
  pushes irrelevant text into the reader.

Reliability History:

- `ReliabilityPanel` builds history from `RELIABILITY_REPORTED` events plus `reliability_report` Artifacts.
- It renders history rows inside a disclosure.
- It does not let users click an older report and read that older report body.
- It shows `reportArtifactId` and sometimes raw ISO `createdAt`, which is useful for debugging but poor for normal use.

Artifact metadata:

- `ArtifactMeta` joins `artifact.kind`, `artifactRole`, `verdict`, and `revisionOf` directly.
- This is why users see `revision / revision of 6a...`.
- The full id should remain inspectable, but it should not be visible in the default deliverable header.

Warnings:

- `WarningCard` is a direct filter over events including `MISSION_PAUSED_RETRYABLE`, `MODEL_TURN_RETRYING`,
  `USER_INPUT_REQUESTED`, and failures.
- There is no active/resolved/archived state.
- Because events are immutable, old warnings remain visible forever.

Time:

- `formatEventTime` uses `Intl.DateTimeFormat(undefined, ...)`, which means browser-local timezone.
- Reliability can show raw `report.createdAt` ISO if the report came from an Artifact instead of an event.
- The product requirement is unified EST/ET display.

## Product Goal

Make the Work Console feel like a premium reading and supervision surface:

1. The first screen answers:
   - What is the Mission?
   - What is happening now?
   - What is the current deliverable?
   - Is anything actively blocking me?

2. The second layer answers:
   - What changed over time?
   - What did each delegate/review/evaluator do?
   - Which evidence or warning caused a decision?

3. Debug-level ids remain accessible only behind explicit details.

## Self-Grilled Decisions

### 1. Is Product History accessible today?

Partially.

Decision:

- Treat current Product History as a good direction but incomplete implementation.
- Backend must guarantee a complete Product-referenced Artifact Index and a way to load one Artifact by id.
- V1 fix should prefer an index-first response:
  - keep event and loaded-content windows bounded,
  - expose every visible Product lineage item as lightweight `artifactIndex`,
  - always load the current deliverable/latest Artifact content,
  - let the user open older drafts, reviews, revisions, or source notes on demand,
  - never silently drop an index row simply because full content was not preloaded.

Model-facing rule:

- Lead Agent should follow the same pattern. It should inspect Product/Artifact titles and summaries first, then open
  the specific Artifact content it needs through an inspect/read tool. Blindly stuffing large historical content into
  every context package is not acceptable.

### 2. Should long Mission prompts remain visible in full?

No.

Decision:

- Mission header shows title plus a short two-line brief.
- Add a `View brief` or `Details` affordance for the full assignment text.
- The full prompt appears in the Mission Info modal, not as a gray wall in the header.
- The header brief should strip repeated whitespace and clamp with a fade or native line clamp.

### 3. Should artifact ids and revision lineage be visible by default?

No.

Decision:

- Default ArtifactMeta should show human labels only:
  - `Draft`
  - `Revision`
  - `Review`
  - `Final`
  - `Search notes`
  - `Quality report`
- `revisionOf`, `artifactId`, `productId`, and raw operation names move to a small `Technical details` disclosure inside
  the selected Artifact section.
- Deliverable header should never show `revision / revision of <id>`.

### 4. Should Reliability History be a list or a reader?

Reader.

Decision:

- Reliability modal shows the latest report by default.
- History rows become selectable compact buttons.
- Selecting a history row swaps the report body to that older report.
- Default history row copy:
  - score pill,
  - status,
  - `ET` time,
  - issue count,
  - no raw report id.
- Raw report id goes into `Technical details`.

### 5. What timezone should Work use?

Eastern Time with explicit `ET` label.

Decision:

- Add shared frontend formatter for Work:
  - `timeZone: "America/New_York"`
  - `hour`, `minute`, `second`
  - label as `ET`.
- Use it for Progress events, Windows, Reliability history, Diagnostics, and Mission metadata.
- Do not show raw ISO timestamps in product UI.

### 6. Should section boundaries be cards, lines, or navigation bands?

Use quieter section bands.

Decision:

- Keep each major surface as a sibling panel, not nested cards.
- Reduce heavy outlines between Product, Windows, Progress, and Diagnostics.
- Use:
  - compact section heading,
  - one hairline divider,
  - slightly different panel background only for active/interactive areas.
- Product deliverable should visually dominate; History/Windows/Progress should feel secondary.

### 7. Should Warnings persist forever?

No.

Decision:

- Derive warning state from events and current Mission state:
  - `active`: unresolved blocker, failed current run/window, waiting input, paused retryable, running error.
  - `resolved`: a later event or current Mission status proves recovery.
  - `archived`: historical retry/noise that never needs default display.
- Default right rail shows only active warnings.
- If there are resolved warnings, show a small `Resolved` disclosure with count.
- Progress still keeps the immutable raw event history.

Resolution examples:

- `MODEL_TURN_RETRYING` becomes resolved when a later `MODEL_TURN_COMPLETED`, `TOOL_CALLED`, or terminal state appears.
- `USER_INPUT_REQUESTED` becomes resolved after `USER_INPUT_RECEIVED`.
- `MISSION_PAUSED_RETRYABLE` becomes resolved after Mission status becomes `running`, `completed`, `blocked`, or `stopped`
  because the user has resumed or the run moved forward.
- `MISSION_FAILED` stays active only when current Mission status is `failed`.

### 8. Should user text be edited or hidden?

Not edited, but summarized and layered.

Decision:

- Preserve exact user instruction in Mission Info.
- Header shows a cleaned, clamped brief.
- Progress `USER_INSTRUCTION_ADDED` rows show a one-line summary and expand for the full text.
- Mission Composer can keep the full input area, but after submission it should not leave a paragraph wall in the main
  reading surface.

## Implementation Plan

### 2026-05-29 Execution Slice

This slice is the production implementation target:

- Landing hero vertical alignment:
  - align the left `Parallex` block around the visual midpoint between the second and third capability cards.
- Mission detail lineage completeness:
  - keep the event window bounded,
  - return a complete lightweight Artifact Index for visible Product lineage,
  - preload only the current deliverable/latest Artifact content and a small recent content window,
  - add an on-demand Artifact read API for older Product History entries.
- Work UI time:
  - introduce one shared ET formatter and use it across event, window, reliability, and diagnostics surfaces.
- Product reader:
  - replace raw implementation metadata with human labels,
  - move ids/revision lineage into `Technical details`,
  - keep History clickable.
- Quality reader:
  - make Reliability History selectable, with latest report as the default,
  - hide raw report ids from default rows.
- Warning rail:
  - derive active/resolved warning state from current Mission status and later events,
  - show only active warnings by default.
- Long assignment text:
  - keep the Mission Header clamped and add a visible details affordance instead of showing a gray paragraph wall.

This slice explicitly does not change evaluator scoring, model prompts, tool execution, or Artifact persistence semantics.

### Phase A: Shared Formatting And Copy Layer

- Add a Work time formatter that returns `hh:mm:ss ET`.
- Replace raw `createdAt` display in Reliability and Windows.
- Replace ArtifactMeta default text with product labels.
- Add Technical details disclosure for ids and operation metadata.

### Phase B: Header And Section Reading Polish

- Clamp Mission goal in `MissionHeader`.
- Add a details button that opens Mission Info.
- Tighten section dividers in CSS.
- Ensure Product remains visually dominant.

### Phase C: Complete History Access

- Backend Mission detail must include a complete Product-referenced Artifact Index for visible Products.
- Product History navigator should show human artifact labels, concise summaries, and `ET` timestamps.
- Full Artifact content is loaded on demand when a user selects an unloaded History row.
- The default Mission detail response must not solve History by preloading hundreds of full text Artifacts.
- Reliability History becomes selectable inside the Quality modal.

### Phase D: Warning State Machine

- Replace `WarningCard` raw event filter with derived warning groups:
  - active,
  - resolved,
  - archived hidden.
- Keep immutable warning events visible in Progress.
- Add tests for common resolution paths.

## Acceptance

- A Mission with more than 20 Artifacts still shows all Product History entries that belong to the current Product.
- Mission detail exposes a lightweight `artifactIndex` so Product History can be complete without preloading every full
  Artifact body.
- Selecting an unloaded Product History row loads the full Artifact through a dedicated API route.
- Product Deliverable no longer displays `revision of <id>` in default view.
- Product History entries are readable, clickable, and use human labels.
- Reliability History rows are clickable/selectable and open the older report body.
- Reliability and Progress timestamps all display `ET`; no raw ISO string appears in the normal Work UI.
- Mission Header clamps long assignment text and exposes the full prompt through details.
- Warnings panel only shows active warnings by default and can show resolved warnings separately.
- Progress remains the immutable audit trail.
- Desktop and mobile screenshots show less gray paragraph mass and clearer section rhythm.
- Frontend build passes.
- Work Mode backend tests pass if Mission detail contract changes.
- Public target smoke confirms no horizontal overflow and no regressions in Product, Quality, and Progress.

## Non-Goals

- Do not change evaluator scoring.
- Do not delete historical events.
- Do not hide Product History.
- Do not remove raw ids from Diagnostics or Technical details.
- Do not implement user acceptance of blocked candidates in this issue.

## Open Follow-Up

- Add paginated Artifact Index search if a Product routinely exceeds the manifest retention window.
