## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 15: Idle Right Rail Information Architecture

## Problem

The Idle right rail drifted into an internal object inspector. It showed conversation `ID` and raw `Count` as large cards at the same priority as the user topic and Brainstorm action.

That is not product-grade for a user-facing control surface. It forces the user to scan implementation details before the action they came for: steering Agents, understanding the topic, and turning useful discussion into a Work Mission.

## Grill

Q: Does the user need the conversation id during normal Idle use?

A: No. It is useful for debugging and support, not for thinking with the Agents. It should be available only behind a compact Debug disclosure.

Q: Does the user need message count?

A: Not in the normal rail. A raw number does not tell the user what to do next. If retained, it belongs in Debug with other support details.

Q: What should the right rail optimize for?

A: Control and continuation. The rail should answer: who is targeted, what are we discussing, can I make a Work brief, and is the session running.

Q: Should Brainstorm move above internal session data?

A: Yes. Brainstorm is the primary product action after topic context. Session status is secondary.

## Decision

Idle right rail default order:

1. Target Agent selection.
2. Topic.
3. Brainstorm / Work brief action.
4. Compact Session status.
5. Collapsed Debug details.

Default view MUST NOT render raw conversation ids or parent ids as primary cards.

Raw message count MAY appear only inside collapsed Debug labeled `Turns`, not as a large object card.

Debug disclosure MAY include:

- conversation id.
- parent idle conversation id when in Companion mode.
- raw visible turn count.

Session owns normal loading and working status. The right rail should not render a second generic `Loading` or `Working` line below Debug unless it is an actual error.

## Acceptance

- Idle right rail no longer shows `ID` or `Count` as standalone cards.
- Brainstorm appears before Session metadata.
- Debug is collapsed by default.
- Conversation ids remain available for debugging after opening Debug.
- Loading and working state are not duplicated outside Session.
- Frontend build passes.
- Public static frontend is updated without restarting backend services when the change is frontend-only.
