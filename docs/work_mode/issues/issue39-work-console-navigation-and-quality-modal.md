## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 39: Work Console Navigation And Quality Modal

## Problem

The selected Mission console still treats the right rail as a permanent Inspector and Quality stack. This is not
product-grade for real use:

- `Inspector / Status` repeats facts the user rarely needs while reading work.
- The right rail should help the user move through the Mission, not force scrolling in the main column.
- Quality reports are important but too heavy as a permanent side card. The current expanded details can become a
  second vertical document beside the real Product.
- Product, Windows, Progress, Diagnostics, and Quality are user tasks. They need navigation affordances, not just
  passive cards.

## Product Goal

Make the Work Console feel like a visual workflow workspace:

1. Left rail remains command-oriented:
   - Project.
   - Mission list.
   - Composer.
   - A small `Info` icon for Mission metadata.

2. Main column remains the reading surface:
   - Activity.
   - Product.
   - Windows.
   - Progress.
   - Diagnostics.

3. Right rail becomes Mission navigation:
   - Click `Activity`, `Product`, `Windows`, `Progress`, `Diagnostics` to scroll the main column.
   - Show concise counts/status for each section.
   - Show a compact Quality button/card that opens details in a modal.

4. Mission metadata moves to an `Info` modal:
   - Project.
   - Lead.
   - Agent count.
   - Current step.
   - Policy.
   - Approval.
   - Current error/busy status.

## Self-Grilled Decisions

### 1. Should Inspector remain permanently visible anywhere?

No.

The always-visible Inspector is debug information, not a daily-use control. It consumes the best secondary rail space
without moving the user forward.

Decision:

- Replace permanent Inspector rail with a small `Info` icon in the left rail header.
- Open metadata in a modal/drawer.
- Keep the same metadata, but make it available on demand.

### 2. Should the right rail become a table of contents?

Yes.

The main Mission column can become long when Product, Windows, Progress, and Diagnostics exist. A Mission-aware table of
contents solves actual navigation friction.

Decision:

- Right rail renders `Mission map`.
- Each row is a button.
- Buttons call `scrollIntoView` for section refs in the main column.
- Rows include counts:
  - Activity: current status.
  - Product: number of Products.
  - Windows: number of Work Windows.
  - Progress: number of visible timeline events.
  - Diagnostics: number of raw events.

### 3. Should Quality be a right-rail card or modal?

Modal.

Quality is a review surface. Users need a compact signal, then a focused detail view when they ask for it. Keeping the
full report permanently in the rail makes the page feel like a risk dashboard and competes with the Product.

Decision:

- Right rail shows one compact Quality row/card:
  - `Risk score`.
  - status.
  - issue count.
  - evidence count.
- Click opens a modal with the existing Reliability report body.
- The modal should be scrollable and focused.

### 4. Should Quality still be available if there is no report?

Yes, but as an empty state.

Decision:

- If no report exists, the Quality card says `No report` and can be disabled or open a short explanation.
- Existing `Check` action remains in `MissionHeader`.

### 5. Should right-rail navigation update the URL?

No for V1.0.x.

Hash routing would interact with existing `/work_project` and `/work_mission` routes. A simple in-page scroll is enough.

### 6. Should mobile show the same right rail?

No.

Mobile should avoid a third column. The Mission map can become a compact horizontal nav below the Mission Header or stack
above Activity.

Decision:

- Desktop: three columns with right Mission map.
- Mobile/tablet: right rail stacks below the header before content, with compact grid rows.

## Component Plan

- `WorkPage`
  - Owns section refs.
  - Passes section counts to a new Mission navigation component.
  - Owns `showMissionInfo` and `showQualityDetails` modal states.

- `ProjectMissionRail`
  - Adds an `Info` icon button near Project/Lead.
  - Keeps Directory and Composer unchanged.

- `InspectorPanel`
  - Refactor from side rail to modal body component.
  - It should not render an `aside` shell by default.

- `ReliabilityPanel`
  - Preserve full report rendering logic.
  - Add compact summary export or prop for modal usage.
  - Compact permanent card should become button-like and open modal.

- New component:
  - `MissionMapPanel.jsx`
  - Renders section buttons and compact Quality trigger.

## Acceptance

- Permanent `Inspector / Status` rail is removed from the desktop right side.
- Left rail has a small `Info` icon for Mission metadata.
- Clicking `Info` opens a modal with the same metadata previously shown by Inspector.
- Right rail lists `Activity`, `Product`, `Windows`, `Progress`, and `Diagnostics`.
- Clicking `Product` scrolls the main column to Product without manual scrolling.
- Quality appears as a compact trigger, not an always-expanded report.
- Clicking Quality opens a modal with the current Reliability details.
- Product remains before Windows and Progress.
- Mobile has no horizontal overflow and does not show three cramped columns.
- Frontend build passes.
- Browser screenshots verify desktop and mobile usability.

## Risks

- Existing tests or smoke scripts may query old `Inspector` text. Update UI smoke if needed.
- `scrollIntoView` can be hidden behind sticky headers. Use nearest section refs and normal block alignment.
- Quality modal must not trap users; include a visible close button and close on overlay click.
- Do not change evaluator scoring or report generation in this UI pass.
