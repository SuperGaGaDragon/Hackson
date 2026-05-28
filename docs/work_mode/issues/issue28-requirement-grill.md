## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 28: Requirement Grill

## Problem

The Lead Agent can start too quickly when the user's request is underspecified.

For high-quality Work Mode output, the Lead should sometimes pause and ask a precise clarifying question before producing work. But it must not become annoying or block progress when the user already grants autonomy.

## Decision

Add a model-visible Requirement Grill protocol to Lead context.

The protocol is a decision rule, not a hidden workflow:

- Ask the user only when a missing decision materially changes the deliverable.
- Ask at most 1-3 focused questions in one `ask_user` turn.
- Each question should explain the tradeoff briefly or include suggested options.
- If the user says `随你`, `不限`, `你决定`, `题材自定`, or equivalent autonomy language, do not ask about that choice.
- If uncertainty is only about preference, choose a strong default and continue.
- If the work is already completed and the user sends a follow-up, clarify only if the follow-up would otherwise cause a wrong revision.

This is inspired by the local `grill-me` skill, but Work Mode must use a bounded product variant. It cannot interrogate indefinitely.

## Self-Grilled Decisions

### Should this be a backend pre-check?

No for V1.0.x.

The product premise is model-selected tools. Backend should expose the rule and validate `ask_user`; the Lead chooses whether to ask.

### Should every Mission start with questions?

No.

That would make Work Mode feel slow and defensive. The Lead should ask only when the missing answer changes execution or acceptance.

### Should Requirement Grill be separate from `ask_user`?

No for now.

`ask_user` is already the correct tool. Requirement Grill changes the Lead's decision criteria and expected question quality.

## Acceptance

- Lead context contains explicit Requirement Grill guidance.
- `ask_user` schema remains unchanged.
- Tests assert the guidance exists and respects autonomy language.
- Existing full smoke still works when the user grants autonomy.
