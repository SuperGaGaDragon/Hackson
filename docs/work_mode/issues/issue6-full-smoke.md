## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 6: Full 8000 CJK Character Smoke

## Problem

A short smoke can prove endpoints but cannot prove the product promise. V1.0 must show that the model can drive a long writing Mission through tools, delegate windows, Products, and final completion.

## Decision

Full 8000 CJK character smoke is mandatory for V1.0 product-ready status.

Fast smoke MAY exist for local debugging, but MUST NOT replace the full smoke.

## Canonical Mission

```text
Title: 写一个8000字小说
Goal: 写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。
Lead: agent_1
Delegate: agent_2
```

## Required Assertions

Backend smoke MUST assert:

- Mission status is `completed`.
- At least one `MISSION_PLAN_UPDATED` event exists.
- At least two delegate Work Windows exist.
- At least one Product exists.
- At least three Artifacts exist.
- `finish_mission` references at least one final Product id.
- Final Artifact exists.
- Final Artifact CJK character count is >= 8000.
- Final Artifact is not only an outline.
- No invalid model turn remains unresolved.

Browser smoke MUST assert:

- Timeline is visible.
- Work Windows are visible and expandable.
- Product Panel shows final Product full content.
- Final Product is highlighted.
- Large text is collapsed by default outside Product Panel.

## CJK Character Count

Machine check SHOULD count characters in:

```text
\u4e00-\u9fff
```

The count SHOULD exclude metadata, titles, plan text, and event messages. It should measure final Artifact content.

## Risks

- Full smoke is slower and costs more.
- Provider timeout can pause Mission.
- Model may finish early with fewer than 8000 CJK chars.
- Model may produce outline only.

## Mitigation

- Mission goal explicitly requires final manuscript.
- `finish_mission` validation can reject final Artifact if count is below threshold for the smoke.
- `paused_retryable` allows resume without losing progress.

## Acceptance

No V1.0 release can be called product-ready until this smoke passes on the target machine or a user-approved equivalent target environment.
