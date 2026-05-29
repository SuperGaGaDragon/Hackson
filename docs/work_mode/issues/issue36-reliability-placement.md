## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 36: Reliability Placement And Quality Status IA

## Problem

Reliability reports are currently rendered as a large main Mission card immediately after Current Activity. That makes
the quality gate feel like the task's primary output. For users, this is backwards: the Work Mode product experience
should foreground the Deliverable, Work Windows, and Progress, while Reliability explains whether the current candidate
is safe to use.

The large report also repeats information already present in Progress and Product History. It is useful, but not always
important enough to occupy the first screen.

## Self-Grilled Decisions

Question: Should Reliability disappear from the UI?

Decision: No. Reliability is a core Work Mode differentiator. It should remain visible, but as a quality status and
expandable review surface rather than a default main-content block.

Question: Should Reliability appear before Product when it blocks a Mission?

Decision: Only as a compact blocker signal. The full report still belongs in an expandable quality drawer. Product and
Deliverable remain the user's primary read surface.

Question: Should Progress still contain Reliability events?

Decision: Yes. Progress is the audit trail and must continue to show evaluator calls and report events through the
Reliability filter.

Question: Where should the full Reliability report live?

Decision: In the right Inspector rail as a compact `Quality` panel with an expandable details drawer. This keeps the
mission body focused and makes quality status continuously visible without forcing a large report into the reading flow.

## Decision

Move the Reliability report out of the main Mission content column.

New Work Console hierarchy:

1. Current Activity.
2. Product Panel.
3. Work Windows.
4. Mission Progress.
5. Diagnostics.

Right rail:

1. Inspector Status.
2. Quality status.
3. Warnings.

Quality status rules:

- If no report exists, show nothing.
- If a report exists, show a compact status row with score, status, confidence, and issue count.
- The row can expand inline to show issues, evidence, claims, limitations, history, and suggested fixes.
- Full report is collapsed by default.
- If a report has blocking/high-risk status, use stronger border color but still keep the content collapsed.

## UI Contract

Reliability Panel MUST NOT render as an always-expanded main Mission card.

Reliability Panel MUST render in the Inspector rail or equivalent side quality surface.

The compact state MUST fit the first viewport and use short labels:

- `Quality`
- `Risk`
- `Needs review`
- `Evidence`

The expanded state MAY show the full report, but it MUST be user-triggered through a native disclosure control or an
equivalent explicit expand action.

## Acceptance

- Main Mission content order no longer includes `.reliability-panel` before Product.
- Product Panel is above Work Windows so the current answer is easier to find.
- Inspector rail shows a compact Quality surface when a Reliability report exists.
- Full Reliability details are collapsed by default.
- Progress Reliability filter still works.
- Public browser smoke verifies no horizontal overflow and that Quality is visible without dominating the Mission body.

## Future Work

- Add a top-of-Deliverable one-line blocker banner when Reliability directly prevents completion.
- Add a first-class `Accept blocked candidate` action after user-acceptance backend support exists.
