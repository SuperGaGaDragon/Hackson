## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Lst Modified by: Codex

# Context Runtime UI Contract

## 1. Purpose

This document defines how the React app should expose Context Runtime state without leaking hidden prompts or raw reasoning.

## 2. User-Facing Surfaces

### Idle

Idle SHOULD show:

- topic.
- Auto state.
- current target Agent.
- visible transcript.
- model failure state.
- queued user interjection while an Agent is generating.
- Brainstorm Card when the user asks to summarize Idle into a Work-ready brief.
- compact session status.

Idle SHOULD NOT show:

- hidden prompt text.
- raw chain-of-thought.
- internal memory candidates.
- one-click Work Mission creation without an editable confirmation step.
- raw conversation ids or parent ids as primary right-rail cards.
- raw message count as a standalone object card.

Idle composer rules:

- The text input remains enabled during generation.
- Sending during generation creates a visible pending user line.
- Auto must pause while a queued user interjection is waiting.
- Tick and Join controls may remain disabled during generation; composer must not.
- The queued line must be sent before the next Auto tick.

Idle Brainstorm Card rules:

- The card belongs in the right rail as a compact action surface, not inside the transcript.
- The card appears before secondary Session metadata in the right rail.
- The card sections are `Topic`, `Key ideas`, `Disagreements`, `Decision`, `Open questions`, and `Suggested Mission`.
- Source message ids should be available behind a compact disclosure surface.
- The suggested Mission title and goal must be editable before Work Mission creation.
- The user must choose an existing Work Project or create a new Project before promotion.
- Promotion creates a draft Mission and does not start execution.

Idle Session rules:

- Auto and current Status may appear as compact metadata.
- Turn count may appear only inside collapsed Debug labeled `Turns`.
- Conversation ids and parent ids belong under a collapsed `Debug` disclosure.
- Normal loading and working state should not be duplicated by a second generic status line below Debug; only actual errors need a separate error line.

### Background Idle

Background Idle belongs in `Me` or Idle settings.

Controls SHOULD show:

- enabled or disabled state.
- short explanation that Agents may continue generating idle turns after the browser is closed.
- budget or cadence summary when available.

Controls MUST NOT imply unlimited background generation.

V1.1 default:

- Background Idle is off for new users.
- Enabling it must be an explicit user action.

### Memory

Memory controls SHOULD eventually show:

- saved memory summary.
- scope.
- enabled or disabled state.
- delete action.
- source count or confidence when space allows.

Memory controls SHOULD NOT expose:

- hidden prompts.
- private provider metadata.
- generic filler memories that do not help the user understand what was learned.
- legacy generic relationship cards such as `Nora and Vale shared another idle interaction.`

Memory controls belong below the primary user and Agent profile editing surface. They should be easy to scan, but they must not occupy the first viewport unless there are urgent review actions.

### Me Page

`Me` SHOULD prioritize:

1. account basics and compact settings.
2. editable Agent profiles.
3. user profile context.
4. memory controls.
5. Debug controls.

Editable Agent profiles are the core daily control surface and MUST appear before Prompt Logs.

Agent `Story` fields SHOULD seed with detailed origin stories for Nora and Vale. Empty or demo-placeholder stories SHOULD normalize to product-grade defaults, while user-authored edits MUST be preserved.

User profile context labels SHOULD use user-facing terms:

- `Style` for the user's own interaction style.
- `Background` for the user's own story/context.
- `Away idle` for browser-closed Background Idle permission.

Avoid showing both user `Personality` and Agent `Personality` as sibling labels because users cannot tell which one they are editing.

### Full Prompt Logging

Full Prompt Logging belongs in the `Me` page.

Controls SHOULD show:

- current enabled or disabled state.
- short explanation that complete model-visible prompt text may include profile, transcript, summary, and memory material.
- retained prompt log count or last retained time when available.
- save action.
- delete retained prompt logs action.

V1.0 default:

- Full Prompt Logging is on for new users.
- The UI must make the default visible in Settings or Debug.
- The user must be able to turn it off before later packages are created.
- Full prompt text is retained for 30 days.
- Turning logging off affects future packages only.
- Deleting retained prompt logs removes full prompt text but keeps Auditable Context Package metadata.

Full Prompt Logging controls SHOULD NOT hide retention behavior or imply that disabling logging deletes existing retained prompt text unless deletion is implemented.

Users MAY view retained full prompt text for their own packages when Full Prompt Logging captured it. Users MUST NOT edit historical full prompt text because it is an audit artifact. Edits to profile, Agent profiles, memory, or logging settings affect future packages instead.

Prompt Logs MUST live under a collapsed `Debug` section by default. The section may show a small count, but raw log rows and hashes must not dominate the main settings viewport. Each retained log SHOULD be expandable so the user can inspect the captured prompt text when debugging.

## 3. Operator Debug Surface

An internal debug view MAY show:

- context package id.
- prompt hash.
- recipe version.
- token estimate.
- included source ids.
- budget decision notes.
- provider response id.
- full prompt text only when the user enabled Full Prompt Logging for that package.

Full prompt text is user-controlled through Full Prompt Logging.

## 4. Failure UX

Stable failure labels:

- `model_rate_limited`
- `model_unavailable`
- `context_package_failed`
- `idle_turn_locked`
- `idle_budget_exhausted`

Frontend must stop Auto after failures that could loop.

## 5. 代办

- Implement V1.0 Me controls for Full Prompt Logging before adding Memory Control.
