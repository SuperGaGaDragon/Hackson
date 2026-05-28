## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 33: Command Rail And Compact Reading UI

## Problem

The current selected Project rail is not product-grade for long Missions.

It mixes four jobs in one vertical stack:

- Project navigation.
- Agent selection.
- Mission directory.
- Mission creation.

The Mission conversation entry points are also scattered. `waiting_input` uses one header form, completed follow-up uses another header form, and running Missions have no direct user message composer. The user cannot build a simple mental model of where to look or where to type.

The second usability failure is long text density. Progress rows, Product summaries, Review rows, and Delegate summaries can become one large paragraph wall. That makes the UI feel like raw model output instead of a controlled work console.

## Product Goal

The left rail SHOULD become a two-zone command surface:

1. Upper zone: `Directory`.
   - Project identity.
   - Back command.
   - Mission list.
   - Compact Agent/Lead indicator.
   - New Mission command.

2. Lower zone: `Composer`.
   - One persistent user input surface for the selected Mission.
   - It adapts to Mission status:
     - `draft`: start or edit/create intent.
     - `running`: add instruction to the Lead.
     - `waiting_input`: answer the Lead's question.
     - `paused`, `paused_retryable`, `failed`, `blocked`, `stopped`: resume with optional instruction.
     - `completed`: continue with the same Lead.

The main console SHOULD prioritize reading and process confidence:

1. Current Activity.
2. Work Windows.
3. Product reader.
4. Compact Progress.
5. Diagnostics.

Mission Header becomes a status/control header, not a text-entry area.

## Hard UI Constraints

- Long generated text MUST NOT render as a default list row.
- List rows MUST show short title, status, time, and one bounded summary line.
- Any text beyond two visual lines MUST be collapsed, clamped, or moved to a reader/detail surface.
- Full deliverable text MUST live in the Product reader.
- Full process payloads MUST live in expanded Progress details or Diagnostics.
- A list item expanding MUST reveal structured details, not a raw unbounded blob.
- The persistent Composer MUST be visually separated from the Directory with sticky bottom placement on desktop.
- The Composer MUST remain usable while the Mission content scrolls.
- The Composer MUST NOT hide Mission history or Product content.
- Mobile MAY stack Directory above Composer, but the Composer must remain near the selected Mission context.

## Self-Grilled Decisions

### 1. Should Agent cards stay large in the rail?

No.

Large Agent cards consume the exact space needed for Mission navigation and the Composer. Agent choice is important at Mission creation time, but less important after a Mission is selected.

Decision:

- Show the current Lead as a compact metadata row.
- Keep Agent switching in the New Mission modal and, if needed, a small selector near the Lead row.
- Do not render two large Agent cards by default in the selected Mission rail.

### 2. Should the Composer live in the left rail or the main header?

Left rail.

The main console should be a reading surface. Putting a large textarea in the header makes every Mission look like a form and pushes the actual work below the fold. A left-bottom Composer creates a stable command zone: find Missions above, direct the Lead below.

Decision:

- Move `waiting_input` answer and completed follow-up UI out of `MissionHeader`.
- Replace them with one rail Composer.
- Keep lifecycle buttons in the header or a compact rail toolbar, but do not duplicate the same primary command in multiple places.

### 3. Should running Missions accept user messages?

Yes, but as first-class Mission events.

Running interruption is valuable only if the backend can preserve it clearly. The user message must not become invisible local state.

Decision:

- V1 implementation MAY limit running messages to "queue instruction for the next Lead turn" if immediate interruption is risky.
- The backend should persist a user instruction event before the next model turn sees it.
- UI copy should be short, such as `Add instruction`, not a long explanation.

### 4. Should failed or paused Missions resume with text?

Yes.

Resume without context is weak after a schema error, budget pause, or user pause. The user should be able to add a short correction while resuming.

Decision:

- Resumable states use the same Composer with a `Resume` action.
- Empty text is allowed for plain resume.
- Non-empty text is persisted as resume instruction before the new run starts.

### 5. Should the rail have a separate chat transcript?

Not in V1.0.x.

A full chat transcript in the rail would compete with Progress and Product. Work Mode is not a chat app; it is a Mission console with a command input.

Decision:

- The rail Composer shows the current prompt/question and input.
- Past user/model interactions remain visible in Progress as compact events.
- Later versions may add a filtered "Conversation" tab only if the event feed becomes too hard to scan.

### 6. How do we solve the "large paragraph wall" problem?

By adding display budgets, not by asking the model to write shorter content.

Decision:

- Components must clamp summaries by CSS and by data mapping.
- Event display helpers should produce concise summaries from payload fields.
- Full content remains accessible through Product, Window, Progress detail, or Diagnostics.
- Any future event card must pass a "two-line default" review before merge.

### 7. Should this be only CSS?

No.

CSS clamping is necessary but insufficient. The component ownership must change so long-form content has a single canonical home.

Decision:

- Introduce a dedicated rail Composer component.
- Refactor Mission Header to status controls only.
- Refactor Mission rows and Progress rows to compact summaries.
- Keep full text in Product and expanded detail components.

## Proposed Desktop Layout

```text
┌────────────────┬──────────────────────────────┬──────────────┐
│ Directory      │ Mission Header               │ Inspector    │
│ Project        │ Current Activity             │ Reliability  │
│ Missions       │ Windows                      │ Warnings     │
│ Lead compact   │ Product Reader               │              │
│ New Mission    │ Progress                     │              │
│                │ Diagnostics                  │              │
│ Composer       │                              │              │
└────────────────┴──────────────────────────────┴──────────────┘
```

Rail behavior:

- Directory scrolls independently when Mission count is high.
- Composer remains pinned at the bottom of the rail on desktop.
- New Mission remains a modal/drawer, not inline rail content.
- Mission rows use fixed height unless selected details are explicitly expanded.

## Component Plan

Frontend ownership:

- `ProjectMissionRail`
  - Owns rail layout and Directory.
  - Renders Mission rows as compact navigation.
  - Renders the new Composer area by composition, not by embedding status-specific forms inline.

- `MissionComposer`
  - New component.
  - Receives Mission status, pending input request, busy state, and text state.
  - Emits one of:
    - answer input request;
    - continue completed Mission;
    - resume with optional instruction;
    - add running instruction.

- `MissionHeader`
  - Shows title, goal, status chip, lifecycle controls, and check control.
  - Does not render textarea forms.

- `ProgressTimeline`
  - Keeps default rows compact.
  - Expanded details remain bounded.

- `eventDisplay`
  - Owns short labels and summary reduction.
  - No component should independently dump raw `event.message` into a large row without truncation.

Backend ownership needed for full Composer:

- Existing:
  - `answer` for `waiting_input`.
  - `follow-up` for `completed`.
  - `start`/resume for resumable states.

- Missing:
  - Persisted user instruction for `running`.
  - Optional resume instruction for paused/failed states if current resume endpoint does not accept it.

V1 implementation may ship visual Composer first for existing supported states, but it MUST NOT fake unsupported states. Unsupported actions should be disabled or explicitly routed through documented backend work.

## Acceptance

Design acceptance:

- A first-time user can identify Mission list and message input within three seconds.
- The rail no longer shows large Agent cards by default.
- The rail does not show permanent Mission creation fields after selection.
- The main header does not contain textarea forms.
- Running, waiting, paused/failed, and completed statuses each have an explicit Composer mode.
- Default Progress, Window, and Product summary rows do not show paragraph walls.
- Full content remains reachable from Product reader or expanded details.

Engineering acceptance:

- Update docs before code.
- Add/keep component README coverage for the new rail and Composer.
- Frontend build passes.
- Browser smoke includes desktop and mobile screenshots.
- Smoke covers:
  - two Missions in one Project remain visible;
  - completed Mission follow-up appears in Composer;
  - waiting input answer appears in Composer;
  - long Progress text is clamped by default and expandable;
  - Product reader still shows full text.

## Risks

- Running-message support may require backend event semantics. Do not fake it in UI.
- Sticky rail Composer can crowd small screens. Mobile must stack cleanly.
- Over-clamping can hide important failure reasons. Failure rows may show a short error code plus expandable details.
- Moving forms out of `MissionHeader` can break existing waiting-input and follow-up tests unless covered intentionally.
