## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 11: Quality Gaming Resistance

## Problem

The Lead can produce a short, source-looking artifact that resembles a reliability-safe answer but does not satisfy the
user's requested deliverable. Example failure shape:

- a few concise paragraphs;
- three recognizable source URLs;
- an `Evidence Ledger` section;
- broad claims that overlap with snippets;
- no real 8,000-word literature-review body, historiographic coverage, or source depth.

This can fool a shallow quality gate because the artifact has evidence-shaped formatting while failing the core product
requirement.

## Product Standard

Evaluator Runtime must judge the evaluated candidate against the user's requested deliverable shape, not against generic
"has citations" signals.

For long-form research or literature-review Missions, a candidate is not close to ship-ready unless it has:

- required body length;
- paper/review prose shape;
- enough source count and source-domain diversity for the requested scale;
- enough citation/source density across the body;
- no evidence-ledger section being used as a substitute for the deliverable.

## Decision

Add deterministic anti-gaming requirements before scoring:

- Extract expected word count from Mission title and goal and keep it as a hard count requirement.
- For paper-like or literature-review goals, require a minimum source count and minimum unique source-domain count.
- For paper-like or literature-review goals, require citation/source density scaled to expected word count.
- Treat `Evidence Ledger` as audit material, not proof of final deliverable quality.
- Keep score secondary. `gateStatus` must stay `repair_required` or `human_review` while these structural requirements
  are missing.

## Non-Goals

- Do not auto-pad content.
- Do not require one exact citation style unless the user requested one.
- Do not replace source-support checks with a subjective essay-quality judge.
- Do not block short research tasks that did not ask for long-form literature-review output.

## Acceptance

- A short French Revolution artifact with three source URLs and an `Evidence Ledger` does not become `ship_ready`.
- The report includes missing/partial requirements for source depth and source density, not just claim support.
- An 8,000-word literature-review Mission with a 400-word candidate remains `repair_required`.
- Existing small research tests still pass when they are not long-form paper-like tasks.
