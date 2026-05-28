## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 30: Evaluator As A Leader Tool

## Problem

Evaluator Runtime currently exists as a route-level action. The user or UI can trigger it, but the Lead Agent cannot choose it inside the Work Mode loop.

That breaks the product thesis:

- The Lead should see a toolbox.
- The Lead should decide when the work needs evaluation.
- The Lead should revise after quality feedback.

## Decision

Add `evaluate_product` as a model-visible Work Mode tool.

It is a backend-owned quality tool. The Lead chooses it, but the backend produces the Reliability Report.

`evaluate_product` MUST:

- Run Evaluator Runtime against the current Mission trace.
- Persist a Reliability Report Artifact.
- Emit `RELIABILITY_REPORTED`.
- Return a bounded observation with score, status, issue counts, top issues, report Artifact id, and a recommended next tool.

`evaluate_product` MUST NOT:

- Modify Product content.
- Finish the Mission.
- Hide limitations.
- Claim proof of correctness.

## Tool Contract

```json
{
  "reason": "string",
  "profile": "research_reliability_v1",
  "productIds": ["string"],
  "artifactIds": ["string"],
  "focus": "string"
}
```

`productIds`, `artifactIds`, and `focus` are hints for the Lead and UI. V1.0 evaluation still reads the full Mission trace and latest final candidate.

## Completion Gate

For research/paper-like Missions, `finish_mission` SHOULD require a current Reliability Report after the latest Product update.

If the latest report has `unsafe_to_ship` or `needs_human_review`, `finish_mission` SHOULD be rejected and the Lead should revise, search, discuss, or ask the user.

This keeps the model flexible while preventing a paper-like research Mission from silently shipping with no evidence or no final draft.

## Acceptance

- `evaluate_product` appears in Lead context and tool schemas.
- The parser accepts a valid `evaluate_product` action.
- The executor persists a Reliability Report Artifact and event.
- The tool observation tells the Lead whether to revise or finish.
- Paper/research completion is blocked when no current report exists or the current report requires human review.
