## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 20: Tool Use Soft Guidance

## Problem
`web_search`, `review_product`, and `discuss_with_delegate` exist as model-visible tools, but real public runs can underuse them because the Lead context only states basic constraints.

The product goal is not to force a fixed workflow. The product goal is to make the Lead aware of when these tools are valuable so the model can choose them more often on tasks that deserve them.

## Decision
Add a `toolUseGuidance` section to the Lead context.

This is soft guidance:

- The backend does not automatically call tools.
- The backend does not reorder the Mission workflow.
- The model still chooses exactly one tool per turn.
- Existing validation and state-machine rules remain authoritative.

## Guidance Rules
- Prefer `web_search` early when the Mission depends on current facts, external references, technical/source-backed claims, named organizations, market data, recent events, or niche facts not present in Product/Artifact context.
- For `web_search`, prefer short 3-6 term queries and leave `allowedDomains` empty unless a domain restriction is essential.
- Prefer `review_product` before `finish_mission` when the Mission has a substantive deliverable and no recent review exists for the final candidate.
- Prefer `discuss_with_delegate` after a review with critical or major findings, after conflicting evidence, or when a second Agent's judgment can improve structure, quality, or tradeoff decisions.
- Prefer `work_product` after `web_search`, `review_product`, or `discuss_with_delegate` when the observation should become user-visible deliverable content.
- Avoid `ask_user` when the Mission already grants autonomy, such as `题材自定` or `不限题材`.

## Non-Goals
- Do not make search mandatory for every Mission.
- Do not make review mandatory for every tiny note.
- Do not make discussion a second hidden model pass.
- Do not add a hidden planner outside the Lead model turn.

## Acceptance
- Lead context includes explicit soft guidance for `web_search`, `review_product`, and `discuss_with_delegate`.
- Lead context tells the model to use short `web_search` queries and avoid unnecessary domain filters.
- Unit tests assert the guidance is present.
- Existing Work Mode full smoke and search smoke still pass.
- Public deployment can use the guidance without data migration.
