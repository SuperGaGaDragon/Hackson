## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 2: Context Budget And Product Retrieval

## Problem

Long Missions create many Artifacts. Blindly including all full content will exceed model context and degrade decisions.

## Decision

V1.0 MUST use Product manifest plus bounded recent Artifact content.

V1.0 MUST provide `inspect_product` as a read-only retrieval tool.

## Risks

- Lead may lose narrative continuity if it cannot see older chapters.
- Context may become too large for full 8000-character smoke.
- Summaries may omit important details.
- Inspect results may duplicate too much UI content.

## Constraints

- Lead context MUST include Product manifest every turn.
- Lead context MUST include budget counters.
- Lead context MUST NOT include all full Artifacts after budget is exceeded.
- `inspect_product` MUST only read current Mission Products and Artifacts.
- `inspect_product` MUST enforce max artifacts and max characters per call.

## Recommended Defaults

Initial defaults can be adjusted after measurement:

```text
recent_full_artifacts = 2
inspect_max_artifacts = 4
inspect_max_chars = 12000
lead_context_recent_events = 20
```

## Acceptance

- A Mission with at least 10 Artifacts can still build context under budget.
- Lead can inspect older Artifact content by id.
- UI can expand inspect events without treating them as the canonical Product content.
