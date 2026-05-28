## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 11: Progress Details And Mission Create Modal

## Problem

The current Work UI still has two product-level usability gaps:

- Progress rows show short event messages but cannot reveal bounded structured details.
- The selected Project rail keeps Mission creation fields visible even after a Mission is selected or completed.

Both make the UI feel less like a focused work console.

## Decision

Progress rows SHOULD expand inline.

Project rail SHOULD hide Mission creation fields behind a `New Mission` button and modal/drawer.

## Progress Detail Rules

Default:

- Compact row only.
- Time and sequence visible.
- Short title and message visible.

Expanded:

- One row expanded at a time.
- Show structured details relevant to the event.
- Never show unbounded final Product text.
- Link to Product reader for full content.

Event-specific detail:

- Plan events show plan steps.
- Tool events show tool name and key arguments.
- Product events show Product/Artifact ids, kind, summary, and bounded excerpt.
- Window events show brief, target, result summary, and linked Artifact.
- Review events show verdict, score, and findings summary.
- Discussion events show participants and summary.

## Create Modal Rules

Default selected Project rail:

- Project title.
- Back button.
- Agent list.
- Mission list.
- `New Mission` command.

Mission creation form:

- Hidden by default.
- Opens as modal or drawer.
- Closes after successful creation.
- Must not remain as permanent rail content after a Mission is selected.

## Acceptance

- Browser smoke can expand a Progress plan row and see its steps.
- Browser smoke can expand a Product event row and see a bounded Artifact summary.
- Browser smoke verifies only one Progress row is expanded at a time.
- Completed Mission rail does not show permanent Mission title/goal inputs.
- `New Mission` opens the create form and creates a Mission successfully.

## Follow-Up

When Review and Discussion tools exist, their Progress details should reuse the same inline expansion pattern.
